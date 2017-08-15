#!/usr/bin/env python3.6


import zabbix_api as api
import json

class ConnectionPool:
    def __init__(self):
        self.connections = []

    def add_connection(self, connection):
        if connection.conn is not None:
            self.connections.append(connection)


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
