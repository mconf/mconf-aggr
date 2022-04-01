import unittest
import unittest.mock as mock

from mconf_aggr.webhook.hook_register import (
    WebhookCreateError,
    WebhookRegister,
    WebhookServer,
)


class WebhookRegisterTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.this_server = "this-server.com"
        cls.single_server = {"https://server1.com": "123"}
        cls.two_servers = {"https://server1.com": "123", "https://server2.com": "234"}
        cls.single_server_return = ["https://server1.com"]
        cls.two_servers_return = ["https://server1.com", "https://server2.com"]

        cls.success_response_xml = r"<response><returncode>SUCCESS</returncode><hookID>1</hookID><permanentHook>false</permanentHook><rawData>false</rawData></response>"
        cls.failed_response_xml = r"<response><returncode>FAILED</returncode><messageKey>missingParamCallbackURL</messageKey><message>You must specify a callbackURL in the parameters.</message></response>"

    def test_create_register_empty_servers(self):
        def populate_servers(cls):
            cls._servers = {}

        with mock.patch(
            "mconf_aggr.webhook.hook_register.WebhookRegister._fetch_servers_from_database"
        ) as fetch_servers_mock:
            fetch_servers_mock.return_value = True
            fetch_servers_mock.side_effect = populate_servers(WebhookRegister)

            register = WebhookRegister(callback_url=self.this_server, servers=[])

        self.assertEqual({}, register.servers)

    def test_create_register_single_server(self):
        register = WebhookRegister(
            callback_url=self.this_server, servers=self.single_server
        )

        self.assertEqual(self.single_server, register.servers)

    def test_create_single_hook(self):
        register = WebhookRegister(
            callback_url=self.this_server, servers=self.single_server
        )

        with mock.patch(
            "mconf_aggr.webhook.hook_register.WebhookServer.create_hook"
        ) as create_hook_mock:
            create_hook_mock.return_value = True
            register.create_hooks()
            success_servers = register.success_servers
            failed_servers = register.failed_servers

        self.assertEqual(self.single_server_return, success_servers)
        self.assertEqual([], failed_servers)

    def test_create_two_hooks(self):
        register = WebhookRegister(
            callback_url=self.this_server, servers=self.two_servers
        )

        with mock.patch(
            "mconf_aggr.webhook.hook_register.WebhookServer.create_hook"
        ) as create_hook_mock:
            create_hook_mock.return_value = True
            register.create_hooks()
            success_servers = register.success_servers
            failed_servers = register.failed_servers

        self.assertEqual(self.two_servers_return, success_servers)
        self.assertEqual([], failed_servers)

    def test_create_two_hooks_failed(self):
        register = WebhookRegister(
            callback_url=self.this_server, servers=self.two_servers
        )

        ServerMock = mock.MagicMock()
        ServerMock.create_hook = mock.MagicMock(side_effect=WebhookCreateError)
        with mock.patch(
            "mconf_aggr.webhook.hook_register.WebhookServer.create_hook",
            ServerMock.create_hook,
        ):
            register.create_hooks()
            success_servers = register.success_servers
            failed_servers = register.failed_servers

        self.assertEqual([], success_servers)
        self.assertEqual(self.two_servers_return, failed_servers)

    def test_build_create_hook_url(self):
        server_addr = next(iter(self.single_server))
        server = WebhookServer(server_addr, "")

        create_hook_url = server._build_create_hook_url()

        self.assertEqual(
            server_addr + "/bigbluebutton/api/hooks/create", create_hook_url
        )

    def test_create_get_request_succeeded(self):
        import requests

        response_mock = mock.MagicMock()
        response_mock.status_code = requests.codes.ok
        response_mock.text = self.success_response_xml
        with mock.patch("mconf_aggr.webhook.hook_register.requests.get") as get_mock:
            get_mock.return_value = response_mock
            server_addr = next(iter(self.single_server))
            server = WebhookServer(server_addr, "")
            r = server.create_hook(callback_url=self.this_server)

        self.assertEqual(r.status_code, requests.codes.ok)

    def test_get_request_failed(self):
        import requests

        response_mock = mock.MagicMock()
        response_mock.status_code = requests.codes.not_found
        response_mock.text = self.success_response_xml
        with mock.patch("mconf_aggr.webhook.hook_register.requests.get") as get_mock:
            get_mock.return_value = response_mock
            server_addr = next(iter(self.single_server))
            server = WebhookServer(server_addr, "")

            with self.assertRaises(WebhookCreateError):
                r = server.create_hook(callback_url=self.this_server)

                self.assertEquals(r.status_code, requests.codes.not_found)
