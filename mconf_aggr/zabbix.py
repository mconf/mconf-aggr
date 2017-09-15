#!/usr/bin/env python3.6


import zabbix_api as api
import psycopg2 as pg
from urllib.parse import urlsplit
from datetime import datetime
import logging

from . import cfg
from .aggregator import AggregatorCallback


class ZabbixLoginError(Exception):
    def __init__(self, msg):
        super().__init__(msg)


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
        self.servers.remove(server)

    def connect(self):
        self.logger.info("Connecting to servers.")
        for server in self.servers:
            try:
                server.connect()
            except ZabbixLoginError:
                self.logger.exception(
                    "Login to server {} has failed. Removing it from server pool." \
                    .format(server)
                )
                self.remove_server(server)

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
        for host in self.hosts.items():
            parameters['hostids'] = host[0]
            try:
                results[host[1]] = self.connection.item.get(parameters)
            except:
                # Suppress stack trace from this exception as it logs
                # many not so useful information.
                self.logger.error(
                    "Something went wrong while getting items from {}." \
                    .format(self)
                )

                # Remove the host from results.
                # Returning None avoids it raising KeyError.
                results.pop(host[1], None)
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


class PostgresConnector:
    def __init__(self, logger=None):
        self.config = cfg.config['database'] # Change it.
        self.conn = None
        self.cursor = None
        self.logger = logger or logging.getLogger(__name__)

    def connect(self):
        self.logger.debug("Connecting to PostgreSQL.")
        try:
            self.conn = pg.connect(host=self.config['host'],
                                   database=self.config['database'],
                                   user=self.config['user'],
                                   password=self.config['password'])

            self.cursor = self.conn.cursor()
        except pg.DatabaseError:
            self.logger.exception(
                "Something went wrong while connecting to the database."
            )

            raise

    def close(self):
        self.logger.info("Closing connection to PostgreSQL.")
        if self.conn is not None:
            self.conn.close()

    def update(self, data):
        update_sql = "UPDATE metrics " \
                     "SET " \
                        "value = %s, " \
                        "updatedat = %s " \
                     "WHERE serverid = %s AND metric = %s"

        try:
            self.cursor.execute(update_sql, (data['value'],
                                             data['updatedat'],
                                             data['serverid'],
                                             data['metric']))
        except DatabaseError:
            self.logger.expcetion("Update to PostgreSQL has failed.")
        else:
            self.conn.commit()


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

    return [{'zabbixserver': server,
             'serverid': host,
             'metric': item['name'],
             'value': item['lastvalue'],
             'updatedat': now} for server, hosts in data.items()
                               for host, items in hosts.items()
                               for item in items]


class ZabbixDataReader():
    def __init__(self, logger=None):
        super().__init__()
        self.pool = None
        self.logger = logger or logging.getLogger(__name__)

    def start(self):
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
