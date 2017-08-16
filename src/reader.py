#!/usr/bin/env python3.6


import zabbix_api as api
import json


class ZabbixConnection:
    def __init__(self, server, login, password):
        self.server = server
        self.login = login
        self.password = password

        # TODO: Make it a dependency.
        self.conn = api.ZabbixAPI(self.server)

        try:
            self.conn.login(self.login, self.password)
        except api.ZabbixAPIException as e:
            print("WARN: Something went wrong while trying to login.")
            print(e.args)

            self.conn = None


class ConnectionPool:
    def __init__(self):
        self.connections = []

    def add_connection(self, connection):
        if connection.conn is not None:
            self.connections.append(connection)


class DataReader:
    def __init__(self, config):
        self.config = config
        self.pool = None
        self.hostids = None

    def connect(self):
        self.pool = ConnectionPool()

        for server in self.config['servers']:
            # It must be more resilient. Surrond it with a try/except.
            self.pool.add_connection(ZabbixConnection(server['url'],
                                                      server['login'],
                                                      server['password']))

    def get_hostids(self):
        application = self.config['application']

        results = conn.conn.host.get({"with_applications": "security"})

        self.hostids = {host['hostid']: host['host'] for host in results}


    def read(self):
        """ Here comes the logic to read data from Zabbix API.
            It iterates over all Zabbix servers reading a subset of the
            monitored items."""
        application = self.config['application']

        for conn in self.pool.connections:
            # Read from Zabbix API.
            results = conn.conn.item.get({"output": "extend", "hostids": self.hostids, "application": "security"})

        return results
