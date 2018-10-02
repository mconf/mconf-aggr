import unittest
import unittest.mock as mock

from mconf_aggr.webhook.hook_register import WebhookRegister, HookCreateError


class WebhookRegisterTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.this_server = "this-server.com"
        cls.single_server = ["https://server1.com"]
        cls.two_servers = ["https://server1.com", "https://server2.com"]

    def test_create_register_empty_servers(self):
        register = WebhookRegister([], callback_url=self.this_server)

        self.assertEquals([], register.servers)

    def test_create_register_single_server(self):
        register = WebhookRegister(self.single_server, callback_url=self.this_server)

        self.assertEquals(self.single_server, register.servers)

    def test_create_single_hook(self):
        register = WebhookRegister(self.single_server, callback_url=self.this_server)

        with mock.patch("mconf_aggr.webhook.hook_register.WebhookRegister.Server.create_hook") as create_hook_mock:
            create_hook_mock.return_value = True
            register.create_hooks()
            success_servers = register.success_servers
            failed_servers = register.failed_servers

        self.assertEquals(self.single_server, success_servers)
        self.assertEquals([], failed_servers)

    def test_create_two_hooks(self):
        register = WebhookRegister(self.two_servers, callback_url=self.this_server)

        with mock.patch("mconf_aggr.webhook.hook_register.WebhookRegister.Server.create_hook") as create_hook_mock:
            create_hook_mock.return_value = True
            register.create_hooks()
            success_servers = register.success_servers
            failed_servers = register.failed_servers

        self.assertEquals(self.two_servers, success_servers)
        self.assertEquals([], failed_servers)

    def test_create_two_hooks_failed(self):
        register = WebhookRegister(self.two_servers, callback_url=self.this_server)

        ServerMock = mock.MagicMock()
        ServerMock.create_hook = mock.MagicMock(side_effect=HookCreateError)
        with mock.patch("mconf_aggr.webhook.hook_register.WebhookRegister.Server.create_hook", ServerMock.create_hook):
            register.create_hooks()
            success_servers = register.success_servers
            failed_servers = register.failed_servers

        self.assertEquals([], success_servers)
        self.assertEquals(self.two_servers, failed_servers)

    def test_build_create_hook_url(self):
        server_addr = self.single_server[0]
        server = WebhookRegister.Server(server_addr)

        create_hook_url = server._build_create_hook_url()

        self.assertEquals(server_addr + "/bigbluebutton/api/hooks/create", create_hook_url)

    def test_create_get_request_succeeded(self):
        import requests
        response_mock = mock.MagicMock()
        response_mock.status_code = requests.codes.ok
        with mock.patch("mconf_aggr.webhook.hook_register.requests.get") as get_mock:
            get_mock.return_value = response_mock
            server_addr = self.single_server[0]
            server = WebhookRegister.Server(server_addr)
            r = server.create_hook(callback_url=self.this_server)

        self.assertEquals(r.status_code, requests.codes.ok)

    def test_get_request_failed(self):
        import requests
        response_mock = mock.MagicMock()
        response_mock.status_code = requests.codes.not_found
        with mock.patch("mconf_aggr.webhook.hook_register.requests.get") as get_mock:
            get_mock.return_value = response_mock
            server_addr = self.single_server[0]
            server = WebhookRegister.Server(server_addr)

            with self.assertRaises(HookCreateError):
                r = server.create_hook(callback_url=self.this_server)

                self.assertEquals(r.status_code, requests.codes.not_found)
