#!/usr/bin/env python3.6


"""This module provides all classes related to the Zabbix API.

It provides the means to fetch data from the Zabbix API on a Zabbix server
that monitors possibly many server hosts and to persist that data into a
database (but it is extensible for other storage systems).

A client of this modules needs only to know its two main classes, namely,
`ZabbixDataReader` and `ZabbixDataWriter`. The former is responsible for
gathering data from a set of Zabbix servers (data regarding their monitored
hosts) and the latter for storing it.

The `ZabbixDataWriter` concrete class implements the `AggregatorCallback`
interface.

The data is retrieved by `ZabbixDataReader` from Zabbix servers in the format::

    {
        "server_1":
        {
            "host_1":
            [
                {"name": "item_1", "lastvalue": "lastvalue_1", ...},
                {"name": "item_2", "lastvalue": "lastvalue_2", ...},
                ...
            ],
            "host_2":
            [
                ...
            ]
        },
        "server_2":
        {
            ...
        }
    }

The data is transformed in this format to be processed by `ZabbixDataWriter`::

    [
        {
            "zabbix_server": "server_1",
            "server_name": "host_1",
            "metric": "item_1",
            "value": "lastvalue_1",
            "updated_at": "<now>"
        },
        {
            "zabbix_server": "server_1",
            "server_name": "host_1",
            "metric": "item_2",
            "value": "lastvalue_2",
            "updated_at": "<now>"
        },
        ...
    ]

This format must be known and respected by the various components that deal
with data inside this module. However, this format does not need to be known
outside the module.
"""

import logging
import reprlib
import sqlalchemy as sa
import time
from contextlib import contextmanager
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from urllib.parse import urlsplit

import cachetools
import zabbix_api as api

from mconf_aggr.aggregator import cfg
from mconf_aggr.aggregator.aggregator import AggregatorCallback, CallbackError
from mconf_aggr.aggregator.utils import time_logger, create_session_scope


class ZabbixLoginError(Exception):
    """Raised if logging in Zabbix server fails.
    """
    pass


class ZabbixNoConnectionError(Exception):
    """Raised if there is not currently active connection to Zabbix server.
    """
    pass


class ServersPool:
    """This class represents the set of Zabbix servers from which data is fetched.

    Attributes
    ----------
    servers : list of ZabbixServer
        List of Zabbix servers from which data should be fetched.
    """
    def __init__(self, logger=None):
        """Constructor of the ServersPool.

        Parameters
        ----------
        logger : logging.Logger
            If not supplied, it will instantiate a new logger from __name__.
        """
        self.servers = []
        self.logger = logger or logging.getLogger(__name__)

        self.logger.info("New pool of servers created.")

    def add_server(self, server):
        """Add a ZabbixServer to the pool.

        Parameters
        ---------
        server : ZabbixServer
            The server to be added to the pool.
        """
        self.logger.debug(f"Adding server {server} to server pool.")
        self.servers.append(server)

    def remove_server(self, server):
        """Remove a ZabbixServer from the pool.

        Parameters
        ---------
        server : ZabbixServer
            The server to be removed from the pool.
        """
        self.logger.info(f"Removing server {server} from server pool.")
        try:
            self.servers.remove(server)
        except:
            self.logger.warn(f"Invalid server {server} to remove.")

    def connect(self, max_retries=3):
        """Connect each ZabbixServer of the pool.

        If a exception occurs while connecting to a given ZabbixServer,
        this server is removed from the pool with no retry.
        """
        self.logger.info(f"Connecting to servers.")
        trying_servers = self.servers.copy()
        retries = 1
        while retries <= max_retries and trying_servers:
            self.logger.warn(f"Trying to connect to servers. Attempt {retries}.")
            success_servers = []
            for server in trying_servers:
                if not server.connected:
                    try:
                        server.connect()
                    except ZabbixLoginError:
                        self.logger.warn(f"Login to server '{server}' has failed.")
                    except Exception as err:
                        self.logger.debug(err)
                    else:
                        success_servers.append(server)

            for server in success_servers:
                if server in trying_servers:
                    trying_servers.remove(server)

            if retries < max_retries and trying_servers:
                # If there is still any retry to do or server to try.
                backoff_delay = 2**(retries)
                self.logger.warn(f"Retrying to connect to servers in {backoff_delay}s.")
                time.sleep(backoff_delay)

            retries += 1

        if trying_servers:
            self.logger.warn("Some Zabbix servers were not able to connect.")
            for failed_server in trying_servers:
                self.remove_server(failed_server)

    def close(self):
        """Close connection of each ZabbixServer of the pool.
        """
        self.logger.info(f"Closing server pool.")
        for server in self.servers:
            server.close()

    def __iter__(self):
        return iter(self.servers)

    def __bool__(self):
        return bool(self.servers)

    def __repr__(self):
        return f"{self.__class__.__name__!s}(servers={reprlib.repr(self.servers)})"


class ZabbixServer:
    """A Zabbix server.

    This class represents a single Zabbix server.
    Do not confuse it with a server host which is any server being monitored.
    Instead, the Zabbix server is the responsible for monitoring hosts.

    Before using an object of this class, one must call `connect()` once
    to create a connection. If it goes well, one can call `get_hosts()` and
    `get_items()` to retrieve data from this server. When it is done, the
    `close()` connection must be called to finish the connection.
    """
    def __init__(self, url, login, password, logger=None):
        """Constructor of the `ZabbixServer`.

        Parameters
        ----------
        url : str
            URL of the server. It must start with 'http://' or 'https://'.
        login : str
            The login that is used to authenticate to the server API.
        password : str
            The password that is used to authenticate to the server API.
        logger : logging.Logger
            If not supplied, it will instantiate a new logger from __name__.
        """
        self.url = url  # It must start with http(s)://.
        self.login = login
        self.password = password
        self.hosts = dict()  # hosts is a hostid:hostname dictionary.
        self.logger = logger or logging.getLogger(__name__)
        self._ok = False

        self.name = urlsplit(self.url).netloc  # Extract just the domain.

        self._item_names_map = {"CPU $2 time": "cpu", "Used memory in %": "mem"}

    def connect(self):
        """Connect to the Zabbix server.

        It tries to connect to the API by performing a regular login.
        """
        self.logger.debug(f"Connecting to server {self}.")
        self.connection = api.ZabbixAPI(self.url, validate_certs=False) # Fix it.

        try:
            self.logger.debug(f"Login to server {self}.")
            with time_logger(self.logger.debug,
                             "Connecting to {server} took {elapsed}s.",
                             server=self):
                self.connection.login(self.login, self.password)
        except api.ZabbixAPIException as err:
            self.logger.error(f"Something went wrong while trying to login to server {self}: {err}.")
            self.connection = None
            self._ok = False

            raise ZabbixLoginError(f"Cannot login to server {self}.") from err
        else:
            self._ok = True

    def close(self):
        """Close the connection to the Zabbix server.

        Currently, nothing must be performed in order to close the connection.
        """
        self.logger.debug(f"Closing server {self}.")

    def get_hosts(self, parameters):
        """Get the hosts being monitored by this Zabbix server.

        Parameters
        ----------
        parameters : dict
            Options that should be passed to the `host.get()` function.

        Raises
        ------
        ZabbixNoConnectionError
            If there is no currently active connection to this server.
        """
        if self.connection is None:
            raise ZabbixNoConnectionError()

        try:
            with time_logger(self.logger.debug,
                             "Getting hosts from {server} took {elapsed}s.",
                             server=self):
                results = self.connection.application.get(parameters)
        except:
            self._ok = False

            raise
        else:
            self.hosts = {host['hostid']: host['host']['host'] for host in results}

    def get_items(self, parameters):
        """Get the items from the hosts being monitored by this Zabbix server.

        Parameters
        ----------
        parameters : dict
            Options that should be passed to the `item.get()` function.

        Returns
        -------
        dict
            A dict in the format "{'this_server': {'host_1': {'item_1': 'value_1', ...}, ...}}"

        Raises
        ------
        Exception
            If anything goes wrong while trying to get items from the hosts.
            The host that caused the exception to be thrown is removed from the
            results.
        """
        self.logger.debug(f"Fetching data from server {self}.")
        if self.connection is None:
            raise ZabbixNoConnectionError()

        results = dict()
        for hostid, host in self.hosts.items():
            parameters['hostids'] = hostid
            try:
                with time_logger(self.logger.debug,
                                 "Getting items from {host} took {elapsed}s.",
                                 host=host):
                    items = self.connection.item.get(parameters)
                    items = self._convert_items_names(items)
                    results[host] = items

            except:
                # Suppress stack trace from this exception as it logs
                # many not so useful information.
                self.logger.error(f"Something went wrong while getting items from {self}.")

                # Remove the host from results.
                # Returning None avoids it raising KeyError.
                # Is it necessary?
                results.pop(host, None)
                self._ok = False

                raise
            else:
                if not self._ok:
                    self.logger.info(f"Connection to server {self} restored.")
                    self._ok = True

        return {self.name: results}

    @property
    def connected(self):
        return self._ok

    def __repr__(self):
        return f"{self.__class__.__name__!s}(url={self.url!r})"

    def __str__(self):
        return self.name

    def _convert_items_names(self, items):
        for item in items:
            old_item_name = item['name']
            if old_item_name in self._item_names_map:
                item['name'] = self._item_names_map[old_item_name]

        return items


Base = declarative_base()
Session = sessionmaker()

session_scope = create_session_scope(Session)

class ServerMetricTable(Base):
    """Table server_metrics in the database.

    Each row in this table represents a single metric retrieved from a Zabbix
    server.
    It inherits from Base - a base class to represent tables by SQLAlchemy.

    Attributes
    ----------
    id : Column of type Integer
        Primary key. Identifier of the metric.
    server_id : Column of type Integer
        Identifier of the monitored server.
    zabbix_server : Column of type String
        Name of the Zabbix server.
    name : Column of type String
        Name of the metric.
    value : Column of type String
        Value of the metric.
    created_at : Column of type DateTime
        Datetime of creation the metric.
    updated_at : Column of type DateTime
        Last datetime the metric was updated.
    """
    __tablename__ = "server_metrics"

    id = sa.Column(sa.Integer, primary_key=True)
    server_id = sa.Column(sa.Integer, sa.ForeignKey("servers.id"))
    zabbix_server = sa.Column(sa.String)
    name = sa.Column(sa.String)
    value = sa.Column(sa.String)
    created_at = sa.Column(sa.DateTime)
    updated_at = sa.Column(sa.DateTime)

    def __repr__(self):
        return (f"{self.__class__.__name__!s}(name={self.name!r}, value={self.value!r}, updated_at={self.updated_at!r})")


class ServerTable(Base):
    """Table servers in the database.

    Each row in this table represents a single server host being monitored.
    It inherits from Base - a base class to represent tables by SQLAlchemy.

    Attributes
    ----------
    id : Column of type Integer
        Primary key. Identifier of the server host.
    name : Column of type String
        Name of the server host.
    """
    __tablename__ = "servers"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    server_metric = sa.orm.relationship("ServerMetricTable")

    def __repr__(self):
        return f"{self.__class__.__name__!s}(name={self.name})"


server_cache = cachetools.TTLCache(maxsize=20, ttl=60)


class ServerMetricDAO:
    """Data Access Object of server metrics.

    It provides the main method to update rows in the server_metrics table.
    """
    def __init__(self, session, logger=None):
        """Constructor of the ServerMetricDAO.

        Parameters
        ----------
        session : sqlalchemy.Session
            Session used by SQLAlchemy to interact with the database.
        logger : logging.Logger
            If not supplied, it will instantiate a new logger from __name__.
        """
        self.session = session
        self.logger = logger or logging.getLogger(__name__)

    def update(self, data):
        """Upinsert the server_metrics table with some new data.

        It does not commit the update. It just add it to be commited.

        Parameters
        ----------
        data : dict
            The data to be updated in the server_metrics table.
            It must include the server host's name, the Zabbix server that
            provided the data, the name of the metric being updated and its
            current value.
        """
        for metric in data:
            server_name, metric_name = metric['server_name'], metric['metric']

            updated_rows = (
                self.session
                .query(ServerMetricTable)
                .filter(
                    ServerTable.name.like(f"%{server_name}%"),
                    ServerMetricTable.name == metric['metric'],
                    ServerTable.id == ServerMetricTable.server_id
                )
                .update(
                    values={ServerMetricTable.value: metric['value'],
                    ServerMetricTable.zabbix_server: metric['zabbix_server'],
                    ServerMetricTable.updated_at: metric['updated_at']},
                    synchronize_session=False
                )
            )

            if updated_rows:
                self.logger.debug(f"Updated metric '{metric_name}' of server '{server_name}'.")
            else:
                server_row = (
                    self.session
                    .query(ServerTable)
                    .filter(ServerTable.name.like(f"%{server_name}%"))
                    .first()
                )

                if server_row:
                    now = datetime.now()
                    new_metric_row = ServerMetricTable(
                        server_id=server_row.id,
                        zabbix_server=metric['zabbix_server'],
                        name=metric['metric'],
                        value=metric['value'],
                        created_at=now,
                        updated_at=now
                    )

                    self.session.add(new_metric_row)

                    self.logger.debug(f"Added new metric '{metric_name}' to server '{server_name}'.")
                else:
                    self.logger.debug(f"Server '{server_name}' not found in database.")


class PostgresConnector:
    """Wrapper of PostgreSQL connection.

    It encapsulates the inner workings of the SQLAlchemy connection process.

    Before using it, one must call once its method `connect()` to configure and
    create a connection to the database. Then, the `update()` method can be
    called for each metric whenever it is necessary to update the database.
    When finished, one must call `close()` to definitely close the connection
    to the database (currently it does nothing).
    """
    def __init__(self, database_uri=None, logger=None):
        """Constructor of the PostgresConnector.

        Parameters
        ----------
        database_uri : str
            URI of the PostgreSQL database instance either local or remote.
        logger : logging.Logger
            If not supplied, it will instantiate a new logger from __name__.
        """
        self.config = cfg.config.zabbix['database']
        self.database_uri = database_uri or self._build_uri()
        self.logger = logger or logging.getLogger(__name__)

    def connect(self):
        """Configure and connect the database.

        It is responsible for creating an engine for the URI provided and
        configure the session.
        """
        self.logger.debug(f"Creating new database session.")
        engine = sa.create_engine(self.database_uri)
        Session.configure(bind=engine)

    def close(self):
        """Close the connection to the database.

        It currently does nothing.
        """
        self.logger.info(f"Closing connection to PostgreSQL. Nothing to do.")
        pass

    def update(self, data):
        """Update the database with new data.

        Parameters
        ----------
        data : dict
            The data to be updated in the database.
        """
        try:
            with session_scope() as session:
                with time_logger(self.logger.debug,
                                 "Database session took {elapsed}s."):
                    self.logger.debug(f"Starting database session.")
                    ServerMetricDAO(session).update(data)
        except sa.exc.OperationalError as err:
            self.logger.error(err)

            raise

    def _build_uri(self):
        user = self.config['user']
        password = self.config['password']
        host = self.config['host']
        database = self.config['database']

        return f"postgresql+psycopg2://{user}:{password}@{host}/{database}"

    def __repr__(self):
        return f"{self.__class__.__name__!s}(database_uri={self.database_uri!r})"


class ZabbixDataWriter(AggregatorCallback):
    """Writer of data retrieved from Zabbix servers.

    This class implements the AggregatorCallback which means its `run()` method
    is intended to run in a separate thread, writing incoming data to the
    database.

    Before using it, one should call its `setup()` method to configure
    any resource used to write data such as database connections etc.
    After that, its `run()` method can be run in a separate thread continuously.
    When finished, its `teardown` can be called to close any opened resource.
    """
    def __init__(self, connector=None, logger=None):
        """Constructor of the ZabbixDataWriter.

        Parameters
        ----------
        connector : Database connector (driver).
            If not supplied, it will instantiate a new `PostgresConnector`.
        logger : logging.Logger
            If not supplied, it will instantiate a new logger from __name__.
        """
        self.connector = connector or PostgresConnector()
        self.logger = logger or logging.getLogger(__name__)

    def setup(self):
        """Setup any resources needed to iteract with the database.
        """
        self.logger.info("Setting up ZabbixDataWriter")
        # Connect to the effective data writer.
        self.connector.connect()

    def teardown(self):
        """Release any resources used to iteract with the database.
        """
        self.logger.info("Tearing down ZabbixDataWriter.")
        self.connector.close()

    def run(self, data):
        """Run main logic of the writer.

        This method is intended to run in a separate thread by the aggregator
        whenever new data must be persisted.

        data : dict
            The data may be compound of many metrics of different server hosts.
        """
        try:
            self.connector.update(data)
        except sa.exc.OperationalError as err:
            self.logger.error(f"Operational error on database.")

            raise CallbackError() from err

    def __repr__(self):
        return f"{self.__class__.__name__!s}(connector={self.connector!r})"


def make_data(data):
    """Transform data into a format that is understandable across the module.

    Parameters
    ----------
    data : dict
        A dict in the format discussed in the module's documentation.

    Returns
    -------
    list
        A list of metrics in the format discussed in the module's documentation.
    """
    now = datetime.now()

    return [{'zabbix_server': server,
             'server_name': host,
             'metric': item['name'],
             'value': item['lastvalue'],
             'updated_at': now}
            for server, hosts in data.items()
            for host, items in hosts.items()
            for item in items]


class ZabbixDataReader():
    """Retriever of the data from Zabbix servers.

    This class is responsible for retrieving data from a pool of Zabbix servers.
    It makes use of the Zabbix API to query and fetch data regarding
    the many monitored hosts from each Zabbix server.
    """
    def __init__(self, logger=None):
        """Constructor of ZabbixDataReader.

        Parameters
        ----------
        pool : ServersPool
            Pool of Zabbix servers from which it retrieves data.
        logger : logging.Logger
            If not supplied, it will instantiate a new logger from __name__.
        """
        super().__init__()
        self.pool = None
        self.logger = logger or logging.getLogger(__name__)

    def setup(self):
        """Setup any resources needed to iteract with the Zabbix servers.

        It mainly setup the servers in its pool, preparing them to serve
        data through the Zabbix API.

        If a Zabbix server fails to get ready, it is removed from the pool.
        """
        self.logger.info(f"Setting up ZabbixDataReader.")
        # Connect to the Zabbix servers of the pool.
        self.connect()

        # Get all hosts of interest in each Zabbix server.
        application = cfg.config.zabbix['application']
        parameters = {'filter': {'name': application}, 'selectHost': {'host': 'host'}}
        failed_servers = []
        for server in self.pool:
            try:
                server.get_hosts(parameters)
            except ZabbixNoConnectionError:
                self.logger.exception(f"No connection to server {server}.")
                failed_servers.append(server)
            except Exception:
                self.logger.error(f"Something went wrong while getting hosts from server {server}.")
                failed_servers.append(server)

        for server in failed_servers:
            self.pool.remove_server(server)

        self.logger.info("ZabbixDataReader running.")

    def stop(self):
        """Release any resources allocated in the setup.

        It basically closes the connection (and releases resources) from
        each of the servers in its pool.
        """
        self.logger.info("Stopping ZabbixDataReader.")
        self.pool.close()
        self.logger.info("ZabbixDataReader stopped.")

    def connect(self):
        """Connect to the Zabbix servers in its pool.

        This method creates a pool of servers and try to connect to them.
        """
        self.logger.info(f"Connecting ZabbixDataReader.")
        # Create a new server pool.
        self.pool = ServersPool()

        self.logger.info(f"Adding servers to the server pool.")
        # Add each server to the server pool.
        for server in cfg.config.zabbix['servers']:
            try:
                url, login, password = (server['url'],
                                        server['login'],
                                        server['password'])
            except KeyError:
                self.logger.exception(f"URL, login or password not supplied for server {server}.")
            else:
                self.pool.add_server(ZabbixServer(url, login, password))

        # Connect the server pool.
        self.pool.connect()

    def read(self):
        """Read data from the Zabbix API.

        This method is the main logic of the reader. It fetches data from
        each of the servers in the pool, prepare data by putting it in a format
        that is understandable by everyone in the module and return this data.

        Returns
        -------
        dict
            A data in the format described in the module's documentation.
        """
        # Here comes the logic to read data from Zabbix API.
        # It iterates over all Zabbix servers reading a subset of the
        # monitored items.
        if not self.pool:
            self.logger.debug("No servers in pool. Nothing to fetch.")
            return None

        self.logger.debug("Fetching data from server pool.")
        application = cfg.config.zabbix['application']
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

    def __repr__(self):
        return f"{self.__class__.__name__!s}(pool={self.pool!r})"
