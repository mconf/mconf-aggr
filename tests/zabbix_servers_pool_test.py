import copy
import unittest
import unittest.mock as mock

import zabbix_api
from mconf_aggr.zabbix.zabbix import ServersPool, ZabbixLoginError, ZabbixNoConnectionError


class TestServersPool(unittest.TestCase):
    def setUp(self):
        self.pool = ServersPool()

    def test_add_server(self):
        n_servers = 10
        self.add_servers(n_servers)

        self.assertEqual(len(self.pool.servers), n_servers)

    def test_remove_server(self):
        n_servers = 3
        self.add_servers(n_servers)

        servers = copy.copy(self.pool.servers)
        for server in servers:
            self.pool.remove_server(server)

        for server in servers:
            self.assertNotIn(server, self.pool.servers)

        self.assertFalse(self.pool.servers)

    def test_connect(self):
        n_servers = 10
        self.add_servers(n_servers)

        self.pool.connect()

        for server in self.pool.servers:
            server.connect.assert_called_once()

    def test_connect_error(self):
        n_servers = 10
        self.add_servers(n_servers)

        servers = copy.copy(self.pool.servers)

        failed_servers = [4, 5, 6, 8]
        success_servers = [i for i in range(n_servers) if i not in failed_servers]

        for server in servers:
            server.connected = False

        for i in failed_servers:
            servers[i].connect = mock.Mock(side_effect=ZabbixLoginError)

        self.pool.connect()

        self.assertEqual(len(self.pool.servers), n_servers-len(failed_servers))

    def test_close(self):
        n_servers = 10
        self.add_servers(n_servers)

        self.pool.close()

        for server in self.pool.servers:
            server.close.assert_called_once()

    def add_servers(self, n_servers):
        servers_mock = [mock.Mock() for _ in range(n_servers)]
        for server_mock in servers_mock:
            self.pool.add_server(server_mock)


class ZabbixServerMock:
    def connect_mock(self):
        print("aqui============================================")
        self._ok = True
