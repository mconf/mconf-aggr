import json
import unittest
import unittest.mock as mock
from unittest.mock import MagicMock, call

import falcon

import mconf_aggr.aggregator.cfg as cfg
from mconf_aggr.webhook.event_listener import (WebhookEventListener,
                                               WebhookEventHandler,
                                               WebhookResponse,
                                               AuthMiddleware,
                                               _normalize_server_url)
from mconf_aggr.webhook.exceptions import WebhookError, RequestProcessingError


class TestListener(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        publisher_mock = mock.Mock()
        cls.channel = 'webhooks'
        cls.event_handler = WebhookEventHandler(publisher_mock, cls.channel)
        cls.event_listener = WebhookEventListener(cls.event_handler)

    def setUp(self):
        cfg.config = {"webhook": {"auth": {"required": True, "tokens": ["123456"]}},
                      "MCONF_WEBHOOK_AUTH_REQUIRED": False}

    def test_listener_on_post_get_params(self):
        req_mock = mock.Mock()
        resp_mock = mock.Mock()

        req_mock.get_param = MagicMock(side_effect=lambda _param: "")

        self.event_listener.on_post(req_mock, resp_mock)

        calls = [call("domain"), call("event")]
        req_mock.get_param.assert_has_calls(calls, any_order=True)

    def test_process_event_fails(self):
        req_mock = mock.Mock()
        resp_mock = mock.Mock()

        self.event_handler.process_event = MagicMock(side_effect=WebhookError)

        self.event_listener.on_post(req_mock, resp_mock)

        event_handler_mock = mock.Mock()
        event_handler_mock.process_event = MagicMock(side_effect=WebhookError)
        self.event_listener.event_handler = event_handler_mock

        self.event_listener.on_post(req_mock, resp_mock)

        resp_body = json.loads(resp_mock.body)

        self.assertEqual(resp_body["status"], "Error")

        self.assertEqual(resp_mock.status, falcon.HTTP_200)

        event_handler_mock.process_event = MagicMock(side_effect=Exception)
        self.event_listener.event_handler = event_handler_mock

        self.event_listener.on_post(req_mock, resp_mock)

        resp_body = json.loads(resp_mock.body)

        self.assertEqual(resp_body["status"], "Error")

        self.assertEqual(resp_mock.status, falcon.HTTP_200)

    def test_process_event_succeeds(self):
        req_mock = mock.Mock()
        resp_mock = mock.Mock()

        event_handler_mock = mock.Mock()
        event_handler_mock.process_event = MagicMock()
        self.event_listener.event_handler = event_handler_mock

        self.event_listener.on_post(req_mock, resp_mock)

        resp_body = json.loads(resp_mock.body)

        self.assertEqual(resp_body["status"], "Success")

        self.assertEqual(resp_mock.status, falcon.HTTP_200)


class TestResponse(unittest.TestCase):
    def setUp(self):
        self.response = WebhookResponse("test message")

    def test_response_success(self):
        self.assertEqual(self.response.success, {"status": "Success", "message": "test message"})

    def test_response_error(self):
        self.assertEqual(self.response.error, {"status": "Error", "message": "test message"})


class TestAuthMiddleware(unittest.TestCase):
    def setUp(self):
        cfg.config = {"webhook": {"auth": {"required": True, "tokens": ["123456"]}},
                      "MCONF_WEBHOOK_AUTH_REQUIRED": True}
        self.auth_middleware = AuthMiddleware()

        self.req_mock = mock.Mock()
        self.resp_mock = mock.Mock()

    def test_auth_no_server_url(self):
        self.req_mock.get_param = lambda _param: None

        with self.assertRaises(falcon.HTTPUnauthorized):
            self.auth_middleware.process_request(self.req_mock, self.resp_mock)

    def test_auth_no_token(self):
        self.req_mock.get_header = lambda _header: None

        with self.assertRaises(falcon.HTTPUnauthorized):
            self.auth_middleware.process_request(self.req_mock, self.resp_mock)

    def test_auth_token_invalid(self):
        self.req_mock.get_param = lambda _param: "my-server.com"
        self.req_mock.get_header = lambda _header: "Bearer 123456"
        self.auth_middleware._token_is_valid = MagicMock(return_value=False)

        with self.assertRaises(falcon.HTTPUnauthorized):
            self.auth_middleware.process_request(self.req_mock, self.resp_mock)

        self.auth_middleware._token_is_valid.assert_called_with("https://my-server.com", "Bearer 123456")

    def test_token_is_valid(self):
        handler_database = {
            "host0": "123",
            "host1": "1234",
            "host2": "102030",
            "localhost": "123456"
        }

        handler_mock = MagicMock()
        handler_mock.secret = lambda h: handler_database[h]

        host = "localhost"
        token = "Bearer 123456"
        self.assertTrue(self.auth_middleware._token_is_valid(host, token, handler_mock))

        host = "host0"
        token = "Bearer 123"
        self.assertTrue(self.auth_middleware._token_is_valid(host, token, handler_mock))

        host = "host1"
        token = "Bearer 123456"
        self.assertFalse(self.auth_middleware._token_is_valid(host, token, handler_mock))

        host = "host2"
        token = "Bearer 123456"
        self.assertFalse(self.auth_middleware._token_is_valid(host, token, handler_mock))


class TestWebhookEventHandler(unittest.TestCase):
    def setUp(self):
        self.channel_mock = mock.Mock()
        self.publisher_mock = mock.Mock()
        self.publisher_mock.publish = mock.MagicMock()
        self.event_handler = WebhookEventHandler(self.publisher_mock, self.channel_mock)
        self.event = '[{"event": 1}, {"event": 2}, {"event": 3}]'

    def test_json_decode_error(self):
        self.event_handler._decode = MagicMock(side_effect=json.JSONDecodeError("", "", 0))

        with self.assertRaises(RequestProcessingError):
            self.event_handler.process_event("localhost", "")

    def test_server_is_normalized(self):
        self.event = '[]'
        with mock.patch("mconf_aggr.webhook.event_listener._normalize_server_url") as normalizer_mock:
            self.event_handler.process_event("localhost", self.event)
            normalizer_mock.assert_called_with("localhost")

    def test_map_fails_publish_not_called(self):
        mapper_mock = mock.MagicMock(side_effect=Exception)
        with mock.patch("mconf_aggr.webhook.event_listener.map_webhook_event", mapper_mock):
            self.event_handler.process_event("localhost", self.event)

        self.event_handler.publisher.publish.assert_not_called()

    def test_publish_called_only_when_valid(self):
        mapped_events = [mapped_1, mapped_2, mapped_3] = [mock.Mock(), None, mock.Mock()]
        mapper_mock = mock.MagicMock(side_effect=mapped_events)
        with mock.patch("mconf_aggr.webhook.event_listener.map_webhook_event", mapper_mock):
            self.event_handler.process_event("localhost", self.event)

            calls = [
                call(mapped_1, channel=self.channel_mock),
                call(mapped_3, channel=self.channel_mock),
            ]

            self.event_handler.publisher.publish.assert_has_calls(calls, any_order=False)

    def test_normalize_server_url(self):
        server_url = "my-server.com"
        self.assertEqual(_normalize_server_url(server_url), "https://my-server.com")

        server_url = "http://my-server.com"
        self.assertEqual(_normalize_server_url(server_url), "http://my-server.com")

        server_url = "https://my-server.com"
        self.assertEqual(_normalize_server_url(server_url), "https://my-server.com")

        server_url = "        my-server.com       "
        self.assertEqual(_normalize_server_url(server_url), "https://my-server.com")
