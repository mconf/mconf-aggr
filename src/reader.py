#!/usr/bin/env python3.6


import zabbix_api as api
import json

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
    def __init__(self, server, login, password):
        self.server = server
        self.login = login
        self.password = password
        """ hosts is a hostid:hostname dictionary. """
        self.hosts = dict()

    def connect(self):
        self.connection = api.ZabbixAPI(self.server)

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
        hostids = list(self.hosts.keys())
        parameters.update({'hostids': hostids})
        results = self.connection.item.get(parameters)

        return results


class DataReader:
    def __init__(self, config):
        self.config = config
        self.pool = None
        self.hostids = None

    def setup(self):
        """ Connect to the Zabbix servers of the pool. """
        self.connect()

        """ Get all hosts of interest in each Zabbix server. """
        application = self.config['application']
        parameters = {"with_applications": application}
        for server in self.pool:
            server.get_hosts(parameters)

    def connect(self):
        self.pool = ServersPool()

        for server in self.config['servers']:
            # It must be more resilient. Surrond it with a try/except.
            self.pool.add_server(ZabbixServer(server['url'],
                                              server['login'],
                                              server['password']))

        self.pool.connect()

    def read(self):
        """ Here comes the logic to read data from Zabbix API.
            It iterates over all Zabbix servers reading a subset of the
            monitored items."""
        application = self.config['application']
        parameters = {"output": ["name"], "application": application}
        all_items = []
        for server in self.pool:
            # Read from Zabbix API.
            server_items = server.get_items(parameters)
            all_items += server_items

        return all_items
