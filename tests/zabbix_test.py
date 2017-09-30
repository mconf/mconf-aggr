#!/usr/bin/env python3.6aggregator_test


import unittest
import unittest.mock as mock

import zabbix_api
from mconf_aggr.zabbix import ZabbixServer, ZabbixLoginError, ZabbixNoConnectionError


class TestZabbixServer(unittest.TestCase):
    def setUp(self):
        self.url = "http://test-zabbix.com/zabbix"
        self.login = "login"
        self.password = "password"
        self.zabbix_server = ZabbixServer(self.url, self.login, self.password)
        
        self.hosts = hosts = {'hostid_1': 'host_1', 'hostid_2': 'host_2'}
        self.parameters = parameters = {'parameter_1': 'value_1'}

    def test_name(self):
        self.assertEquals(self.zabbix_server.name, "test-zabbix.com")

    def test_login_called(self):
        with mock.patch("zabbix_api.ZabbixAPI") as ZabbixAPI_mock:
            connection_mock = ZabbixAPI_mock.return_value
            self.zabbix_server.connect()
            connection_mock.login.assert_called_with(self.login, self.password)

            self.assertTrue(self.zabbix_server._ok)

    def test_login_error(self):
        with mock.patch("zabbix_api.ZabbixAPI") as ZabbixAPI_mock:
            connection_mock = ZabbixAPI_mock.return_value
            connection_mock.login = mock.Mock(side_effect=zabbix_api.ZabbixAPIException)

            with self.assertRaises(ZabbixLoginError):
                self.zabbix_server.connect()

            self.assertIsNone(self.zabbix_server.connection)
            self.assertFalse(self.zabbix_server._ok)

    def test_get_hosts(self):
        results = [{'hostid': 'hostid_1', 'host': 'host_1'},
                   {'hostid': 'hostid_2', 'host': 'host_2'}]

        self.zabbix_server.connection = mock.Mock()
        self.zabbix_server.connection.host = mock.Mock()
        self.zabbix_server.connection.host.get.return_value = results

        self.zabbix_server.get_hosts(self.parameters)

        self.zabbix_server.connection.host.get.assert_called_with(self.parameters)

        self.assertEquals(self.zabbix_server.hosts, self.hosts)


    def test_get_hosts_connection_none(self):
        self.zabbix_server.connection = None

        with self.assertRaises(ZabbixNoConnectionError):
            self.zabbix_server.get_hosts(self.parameters)

    def test_get_hosts_get_error(self):
        self.zabbix_server.connection = mock.Mock()
        self.zabbix_server.connection.host = mock.Mock()
        self.zabbix_server.connection.host.get = mock.Mock(side_effect=Exception)

        with self.assertRaises(Exception):
            self.zabbix_server.get_hosts(self.parameters)

        self.zabbix_server.connection.host.get.assert_called_with(self.parameters)

        self.assertFalse(self.zabbix_server.hosts)

        self.assertFalse(self.zabbix_server._ok)

    def test_get_items(self):
        self.zabbix_server.hosts = self.hosts
        items = {self.zabbix_server.name: {'host_1': 'result', 'host_2': 'result'}}

        self.zabbix_server.connection = mock.Mock()
        self.zabbix_server.connection.item = mock.Mock()
        self.zabbix_server.connection.item.get.return_value = "result"

        returned_items = self.zabbix_server.get_items(self.parameters)

        self.parameters['hostid_1'] = 'host_1'
        self.zabbix_server.connection.item.get.assert_called_with(self.parameters)

        self.parameters['hostid_2'] = 'host_2'
        self.zabbix_server.connection.item.get.assert_called_with(self.parameters)

        self.assertEquals(self.zabbix_server.get_items(self.parameters), items)

        self.assertTrue(self.zabbix_server._ok)

    def test_get_items_connection_none(self):
        self.zabbix_server.connection = None

        with self.assertRaises(ZabbixNoConnectionError):
            self.zabbix_server.get_items(self.parameters)

    def test_get_items_get_error(self):
        self.zabbix_server.hosts = {'hostid_1': 'host_1', 'hostid_2': 'host_2'}

        self.zabbix_server.connection = mock.Mock()
        self.zabbix_server.connection.item = mock.Mock()
        self.zabbix_server.connection.item.get = mock.Mock(side_effect=Exception)

        with self.assertRaises(Exception):
            self.zabbix_server.get_items(self.parameters)

        self.assertFalse(self.zabbix_server._ok)
