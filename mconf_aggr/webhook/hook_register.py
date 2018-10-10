import hashlib
import logging
import requests
import urllib.parse
from urllib.parse import urljoin
from xml.etree import ElementTree

from mconf_aggr.webhook.database_handler import WebhookServerHandler


class WebhookCreateError(Exception):
    def __init__(self, reason="unexpected reason"):
        self.reason = reason


class WebhookAlreadyExistsError(Exception):
    def __init__(self):
        self.reason = "webhook already exists"

class WebhookRegister:
    def __init__(self, servers, callback_url, get_raw=False, hook_id=None, logger=None):
        self._callback_url = callback_url
        self._get_raw = get_raw
        self._hook_id = hook_id
        self._success_servers = []
        self._failed_servers = []

        self.logger = logger or logging.getLogger(__name__)

        handler = WebhookServerHandler()
        servers = handler.servers()

        self._servers = {}
        for server in servers:
            self._servers[server.name] = server.secret

    @property
    def servers(self):
        return self._servers

    @property
    def success_servers(self):
        return self._success_servers

    @property
    def failed_servers(self):
        return self._failed_servers

    def create_hooks(self):
        for server, token in self._servers.items():
            inner_server = WebhookServer(server, token)
            try:
                _ = inner_server.create_hook(self._callback_url, self._get_raw, self._hook_id)
            except WebhookCreateError as err:
                self.logger.warn(f"Webhook registration for server '{server}' failed ({err.reason}).")

                self.failed_servers.append(server)
            except WebhookAlreadyExistsError as err:
                self.logger.info(f"Webhook registration for server '{server}' ok (webhook already exists).")
            except Exception as err:
                self.logger.warn(f"Webhook registration for server '{server}' failed (unexpected reason).")

                self.failed_servers.append(server)
            else:
                self.logger.info(f"Webhook registration for server '{server}' ok.")

                self.success_servers.append(server)


class WebhookServer:
    def __init__(self, server, secret, logger=None):
        self._server = server
        self._secret = secret

        self.logger = logger or logging.getLogger(__name__)

    def create_hook(self, callback_url, get_raw=False, hook_id=None):
        hook_url = self._build_create_hook_url()
        params = {"callbackURL": callback_url, "getRaw": get_raw}
        if hook_id:
            params["hookID"] = hook_id

        params["checksum"] = checksum("hooks/create", urllib.parse.urlencode(params), self._secret)

        r = None
        try:
            r = requests.get(hook_url, params=params)
            self.logger.debug(f"webhook server: '{hook_url}'\nresponse: '{r.text}'.")
        except requests.exceptions.ConnectionError as err:
            raise WebhookCreateError("connection error") from err
        except Exception as err:
            raise WebhookCreateError(str(err)) from err
        else:
            try:
                parse_response(r)
            except (WebhookCreateError, WebhookAlreadyExistsError) as err:
                raise err
            except Exception as err:
                raise WebhookCreateError()

    def _build_create_hook_url(self):
        return urljoin(self._server, "bigbluebutton/api/hooks/create")


def checksum(method, params, secret):
    encoded_payload = method.encode("utf-8") + params.encode("utf-8") + secret.encode("utf-8")
    sha1_payload = hashlib.sha1(encoded_payload)

    return sha1_payload.hexdigest()


def parse_response(response):
    if response.status_code == requests.codes.ok:
        try:
            response_xml = ElementTree.fromstring(response.text)
        except Exception as err:
            raise WebhookCreateError() from err
        else:
            return_code_node = response_xml.find("returncode")
            message_key_node = response_xml.find("messageKey")
            return_code = return_code_node.text if return_code_node is not None else None
            message_key = message_key_node.text if message_key_node is not None else None

            if return_code == "SUCCESS" and message_key == "duplicateWarning":
                raise WebhookAlreadyExistsError()
            elif return_code == "FAILED" and message_key == "checksumError":
                raise WebhookCreateError("checksum error")
            elif return_code == "FAILED" and message_key is not None:
                raise WebhookCreateError(message_key)
            elif return_code == "FAILED":
                raise WebhookCreateError()
            elif return_code != "SUCCESS":
                raise WebhookCreateError(return_code.text)
            elif not return_code and not message_key:
                raise WebhookCreateError()
    else:
        raise WebhookCreateError(f"status code: {response.status_code}")
