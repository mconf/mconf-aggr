import hashlib
import logging
import requests
import urllib.parse
from urllib.parse import urljoin
from xml.etree import ElementTree

from mconf_aggr.webhook.database_handler import WebhookServerHandler

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
            except HookCreateError as err:
                self.logger.warn(f"Webhook registration for server '{server}' failed.")

                self.failed_servers.append(server)
            except Exception as err:
                self.logger.warn(f"Webhook registration for server '{server}' failed.")
                self.logger.warn("An exceptional error occurred when trying to register webhooks.")
                self.logger.debug(err)

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
        except requests.exceptions.ConnectionError as err:
            self.logger.warn(f"Connection error with '{hook_url}'.")

            raise HookCreateError from err
        except Exception as err:
            self.logger.warn(f"An unexpected error occurred with '{hook_url}'.")

            raise HookCreateError from err
        else:
            try:
                success = parse_response(r)
            except WebhookAlreadyExistsError as err:
                self.logger.info(f"Webhook registration to '{self._server}' failed.")

                raise HookCreateError()
                if success:
                    self.logger.info(f"Webhook registered successfuly to '{self._server}'.")
                else:
                    self.logger.info(f"Webhook registration to '{self._server}' failed.")

                    raise HookCreateError()

    def _build_create_hook_url(self):
        return urljoin(self._server, "bigbluebutton/api/hooks/create")


class HookCreateError(Exception):
    pass


def checksum(method, params, secret):
    encoded_payload = method.encode("utf-8") + params.encode("utf-8") + secret.encode("utf-8")
    sha1_payload = hashlib.sha1(encoded_payload)

    return sha1_payload.hexdigest()


def parse_response(response):
    if response.status_code == requests.codes.ok:
        response_xml = ElementTree.fromstring(response.text)
        return_code = response_xml.find("returncode").text
        message_key = response_xml.find("messageKey").text

        if message_key == "duplicateWarning": return False

        return True if return_code == "SUCCESS" else False
    else:
        return False
