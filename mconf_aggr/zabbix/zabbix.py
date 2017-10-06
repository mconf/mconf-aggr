#!/usr/bin/env python3.6


import logging
import sqlalchemy as sa
from contextlib import contextmanager
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from urllib.parse import urlsplit

import psycopg2 as pg
import zabbix_api as api

from mconf_aggr import cfg
from mconf_aggr.aggregator import AggregatorCallback


class ZabbixLoginError(Exception):
    pass


class ZabbixNoConnectionError(Exception):
    pass


class ServersPool:
    def __init__(self, logger=None):
        self.servers = []
        self.logger = logger or logging.getLogger(__name__)

        self.logger.info("New pool of servers created.")

    def add_server(self, server):
        self.logger.debug("Adding server {} to server pool.".format(server))
        self.servers.append(server)

    def remove_server(self, server):
        self.logger.info("Removing server {} from server pool.".format(server))
        try:
            self.servers.remove(server)
        except:
            self.logger.warn("Invalid server {} to remove.".format(server))

    def connect(self):
        self.logger.info("Connecting to servers.")
        failed_servers = []
        for server in self.servers:
            try:
                server.connect()
            except ZabbixLoginError:
                self.logger.exception(
                    "Login to server {} has failed. Removing it from server pool." \
                    .format(server)
                )
                failed_servers.append(server)

        for failed_server in failed_servers:
            self.remove_server(failed_server)

    def close(self):
        self.logger.info("Closing server pool.")
        for server in self.servers:
            server.close()

    def __iter__(self):
        return iter(self.servers)


class ZabbixServer:
    def __init__(self, url, login, password, logger=None):
        self.url = url # It must start with http(s)://.
        self.login = login
        self.password = password
        self.hosts = dict() # hosts is a hostid:hostname dictionary.
        self.logger = logger or logging.getLogger(__name__)
        self._ok = False

        self.name = urlsplit(self.url).netloc # Extract just the domain.

    def connect(self):
        self.logger.debug("Connecting to server {}.".format(self))
        self.connection = api.ZabbixAPI(self.url)

        try:
            self.logger.debug("Login to server {}.".format(self))
            self.connection.login(self.login, self.password)
        except api.ZabbixAPIException:
            self.logger.exception(
                "Something went wrong while trying to login to server {}." \
                .format(self)
            )
            self.connection = None
            self._ok = False

            raise ZabbixLoginError("Can not login to server".format(self))
        else:
            self._ok = True

    def close(self):
        self.logger.debug("Closing server {}.".format(self))

    def get_hosts(self, parameters):
        if self.connection is None:
            raise ZabbixNoConnectionError()

        try:
            results = self.connection.host.get(parameters)
        except:
            self._ok = False

            raise
        else:
            self.hosts = {host['hostid']: host['host'] for host in results}

    def get_items(self, parameters):
        self.logger.debug("Fetching data from server {}.".format(self))
        if self.connection is None:
            raise ZabbixNoConnectionError()

        results = dict()
        for hostid, host in self.hosts.items():
            parameters['hostids'] = hostid
            try:
                results[host] = self.connection.item.get(parameters)
            except:
                # Suppress stack trace from this exception as it logs
                # many not so useful information.
                self.logger.error(
                    "Something went wrong while getting items from {}." \
                    .format(self)
                )

                # Remove the host from results.
                # Returning None avoids it raising KeyError.
                # Is it necessary?
                results.pop(host, None)
                self._ok = False

                raise
            else:
                if not self._ok:
                    self.logger.info("Connection to server {} restored." \
                                     .format(self))
                    self._ok = True

        return {self.name: results}

    def __str__(self):
        return self.name


Base = declarative_base()
Session = sessionmaker()


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


class ServerMetricTable(Base):
    __tablename__ = "server_metrics"

    id = sa.Column(sa.Integer, primary_key=True)
    server_id = sa.Column(sa.Integer)
    zabbix_server = sa.Column(sa.String)
    name = sa.Column(sa.String)
    value = sa.Column(sa.String)
    created_at = sa.Column(sa.Time)
    updated_at = sa.Column(sa.Time)

    def __repr__(self):
        return "<ServerMetric(name={}, value={}m, updated_at={})" \
                .format(self.name, self.value, self.updated_at)


class ServerTable(Base):
    __tablename__ = "servers"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)

    def __repr__(self):
        return "<Server(name={})".format(self.name)


class ServerMetricDAO:
    def __init__(self, session):
        self.session = session

    def update(self, data):
        server_id = self.session.query(ServerTable).filter(ServerTable.name == data['server_name']).first()

        metric = self.session.query(ServerMetricTable) \
                             .filter(ServerMetricTable.server_id == server_id.id,
                                     ServerMetricTable.name == data['metric']) \
                             .first()

        if metric:
            metric.value = data['value']
            metric.zabbix_server = data['zabbix_server']
            metric.updated_at = data['updatedat']
        else:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            metric = ServerMetricTable(server_id=server_id.id,
                                       zabbix_server=data['zabbix_server'],
                                       name=data['metric'],
                                       value=data['value'],
                                       created_at=now,
                                       updated_at=now)

        self.session.add(metric)


class PostgresConnector:
    def __init__(self, database_uri, logger=None):
        self.config = cfg.config['database'] # Change it.
        self.database_uri = database_uri
        self.logger = logger or logging.getLogger(__name__)

    def connect(self):
        self.logger.debug("Creating new database session.")
        engine = sa.create_engine(self.database_uri)
        Session.configure(bind=engine)

    def close(self):
        self.logger.info("Closing connection to PostgreSQL. Nothing to do.")
        pass

    def update(self, data):
        with session_scope() as session:
            ServerMetricDAO(session).update(data)


class ZabbixDataWriter(AggregatorCallback):
    def __init__(self, connector=None, logger=None):
        self.connector = connector or PostgresConnector()
        self.logger = logger or logging.getLogger(__name__)

    def setup(self):
        self.logger.info("Setting up ZabbixDataWriter")
        # Connect to the effective data writer.
        self.connector.connect()

    def teardown(self):
        self.logger.info("Tearing down ZabbixDataWriter.")
        self.connector.close()

    def run(self, data):
        for metric in data:
            self.connector.update(metric)


def make_data(data):
    metrics = []
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    return [{'zabbix_server': server,
             'server_name': host,
             'metric': item['name'],
             'value': item['lastvalue'],
             'updated_at': now} for server, hosts in data.items()
                                for host, items in hosts.items()
                                for item in items]


class ZabbixDataReader():
    def __init__(self, logger=None):
        super().__init__()
        self.pool = None
        self.logger = logger or logging.getLogger(__name__)

    def setup(self):
        self.logger.info("Setting up ZabbixDataReader.")
        # Connect to the Zabbix servers of the pool.
        self.connect()

        # Get all hosts of interest in each Zabbix server.
        application = cfg.config['application']
        parameters = {"with_applications": application}
        for server in self.pool:
            try:
                server.get_hosts(parameters)
            except ZabbixNoConnectionError:
                self.logger.exception(
                    "No connection to server {}.".format(server)
                )
                self.pool.remove_server(server)
            except Exception:
                self.logger.exception(
                    "Something went wrong when getting hosts for server {}." \
                    .format(server)
                )
                self.pool.remove_server(server)

        self.logger.info("ZabbixDataReader running.")

    def stop(self):
        self.logger.info("Stopping ZabbixDataReader.")
        self.pool.close()

    def connect(self):
        self.logger.info("Connecting ZabbixDataReader.")
        # Create a new server pool.
        self.pool = ServersPool()

        self.logger.info("Adding servers to the server pool.")
        # Add each server to the server pool.
        for server in cfg.config['servers']:
            try:
                url, login, password = server['url'], \
                                       server['login'], \
                                       server['password']
            except KeyError:
                self.logger.exception(
                    "URL, login or password not supplied for server {}". \
                    format(server)
                )
            else:
                self.pool.add_server(ZabbixServer(url, login, password))

        # Connect the server pool.
        self.pool.connect()

    def read(self):
        # Here comes the logic to read data from Zabbix API.
        # It iterates over all Zabbix servers reading a subset of the
        # monitored items.
        self.logger.debug("Fetching data from server pool.")
        application = cfg.config['application']
        parameters = {"output": ["hostid", "name", "lastvalue"],
                      "application": application}
        all_items = dict()

        # Fetch data from each server in the server pool.
        for server in self.pool:
            try:
                all_items.update(server.get_items(parameters))
            except:
                pass

        # Create a single bundle of data.
        data = make_data(all_items)

        return data
