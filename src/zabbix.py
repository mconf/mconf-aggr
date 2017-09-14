#!/usr/bin/env python3.6


import zabbix_api as api
import psycopg2 as pg
from urllib.parse import urlsplit
from datetime import datetime
import logging

import cfg
from aggregator import AggregatorCallback


class ServersPool:
    def __init__(self, logger=None):
        self.servers = []
        self.logger = logger or logging.getLogger(__name__)

        self.logger.info("New pool of servers created.")

    def add_server(self, server):
        self.logger.info("Adding server {} to server pool.".format(server))
        self.servers.append(server)

    def connect(self):
        self.logger.info("Connecting to servers.")
        for server in self.servers:
            server.connect()

    def __iter__(self):
        return iter(self.servers)


class ZabbixServer:
    def __init__(self, url, login, password, logger=None):
        self.url = url # It must start with http(s)://.
        self.name = urlsplit(self.url).netloc # Extract just the domain.
        self.login = login
        self.password = password
        self.hosts = dict() # hosts is a hostid:hostname dictionary.
        self.logger = logger or logging.getLogger(__name__)

    def connect(self):
        self.logger.info("Connecting to server {}".format(self))
        self.connection = api.ZabbixAPI(self.url)

        try:
            self.logger.debug("Login to server {}.".format(self))
            self.connection.login(self.login, self.password)
        except api.ZabbixAPIException as err:
            self.logger.exception(
                "Something went wrong while trying to login to server {}." \
                .format(self)
            )

            self.connection = None

    def get_hosts(self, parameters):
        results = self.connection.host.get(parameters)
        self.hosts = {host['hostid']: host['host'] for host in results}

    def get_items(self, parameters):
        results = dict()
        for host in self.hosts.items():
            parameters['hostids'] = host[0]
            results[host[1]] = self.connection.item.get(parameters)

        return {self.name: results}


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
        except pg.DatabaseError as err:
            self.logger.exception(
                "Something went wrong while connecting to the database."
            )

    def close(self):
        self.logger.info("Closing connection to PostgreSQL.")
        if self.conn is not None:
            self.conn.close()

    def update(self, data):
        update_sql = """UPDATE metrics
                        SET
                            value = %s,
                            updatedat = %s
                        WHERE serverid = %s AND metric = %s"""

        self.cursor.execute(update_sql, (data['value'],
                                         data['updatedat'],
                                         data['serverid'],
                                         data['metric']))

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

    def setup(self):
        self.logger.info("Setting up ZabbixDataReader.")
        # Connect to the Zabbix servers of the pool.
        self.connect()

        # Get all hosts of interest in each Zabbix server.
        application = cfg.config['application']
        parameters = {"with_applications": application}
        for server in self.pool:
            server.get_hosts(parameters)

    def connect(self):
        self.logger.info("Connecting ZabbixDataReader.")
        # Create a new server pool.
        self.pool = ServersPool()

        # Add each server to the server pool.
        for server in cfg.config['servers']:
            # It must be more resilient. Surrond it with a try/except.
            self.pool.add_server(ZabbixServer(server['url'],
                                              server['login'],
                                              server['password']))

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
            all_items.update(server.get_items(parameters))

        # Create a single bundle of data.
        data = make_data(all_items)

        return data
