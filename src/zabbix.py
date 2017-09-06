#!/usr/bin/env python3.6


import zabbix_api as api
import psycopg2 as pg
from urllib.parse import urlsplit
from datetime import datetime
import time

import cfg
from aggregator import AggregatorCallback
from dummy import DummyWriter


class ServersPool:
    def __init__(self):
        self.servers = []

    def add_server(self, server):
        self.servers.append(server)

    def connect(self):
        for server in self.servers:
            server.connect()

    def __iter__(self):
        return iter(self.servers)


class ZabbixServer:
    def __init__(self, url, login, password):
        self.url = url # It must start with http(s)://.
        self.name = urlsplit(self.url).netloc # Extract just the domain.
        self.login = login
        self.password = password
        self.hosts = dict() # hosts is a hostid:hostname dictionary.

    def connect(self):
        self.connection = api.ZabbixAPI(self.url)

        try:
            self.connection.login(self.login, self.password)
        except api.ZabbixAPIException as e:
            print("WARN: Something went wrong while trying to login.")
            print(e.args)

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
    def __init__(self):
        self.config = cfg.config['database'] # Change it.
        self.conn = None
        self.cursor = None

    def connect(self):
        try:
            self.conn = pg.connect(host=self.config['host'],
                                   database=self.config['database'],
                                   user=self.config['user'],
                                   password=self.config['password'])

            self.cursor = self.conn.cursor()
        except pg.DatabaseError as e:
            print(e)

    def close(self):
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
    def __init__(self, connector=None):
        """ Should it be called 'driver'? """
        self.connector = connector or PostgresConnector()

    def setup(self):
        """ Here we must setup the DB driver from the config file. """
        self.connector.connect()

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
    def __init__(self):
        super().__init__()
        self.pool = None

    def setup(self):
        """ Connect to the Zabbix servers of the pool. """
        self.connect()

        """ Get all hosts of interest in each Zabbix server. """
        application = cfg.config['application']
        parameters = {"with_applications": application}
        for server in self.pool:
            server.get_hosts(parameters)

    def connect(self):
        self.pool = ServersPool()

        for server in cfg.config['servers']:
            # It must be more resilient. Surrond it with a try/except.
            self.pool.add_server(ZabbixServer(server['url'],
                                              server['login'],
                                              server['password']))

        self.pool.connect()

    def read(self):
        """ Here comes the logic to read data from Zabbix API.
            It iterates over all Zabbix servers reading a subset of the
            monitored items."""
        application = cfg.config['application']
        parameters = {"output": ["hostid", "name", "lastvalue"],
                      "application": application}
        all_items = dict()
        for server in self.pool:
            all_items.update(server.get_items(parameters))

        data = make_data(all_items)

        return data
