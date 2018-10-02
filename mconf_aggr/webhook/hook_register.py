import hashlib
import logging
import requests
import urllib.parse
import xml.etree.ElementTree as ET
from urllib.parse import urljoin

class WebhookRegister:
    class Server:
        def __init__(self, server, secret, logger=None):
            self._server = server
            self._secret = secret
            self.logger = logger or logging.getLogger(__name__)

        def create_hook(self, callback_url, get_raw=False, hook_id=None):
            hook_url = self._build_create_hook_url()
            params = {"callbackURL": callback_url, "getRaw": get_raw}
            if hook_id:
                params["hookID"] = hook_id

            checksum = hashlib.sha1("hooks/create".encode("utf-8") + urllib.parse.urlencode(params).encode("utf-8") + self._secret.encode("utf-8"))
            params["checksum"] = checksum.hexdigest()

            r = None
            try:
                r = requests.get(hook_url, params=params)
            except requests.exceptions.ConnectionError as err:
                self.logger.warn(err)
            else:
                if r.status_code == requests.codes.ok:
                    import xml.etree.ElementTree as ET

                    response_xml = ET.fromstring(r.text)
                    return_code = response_xml.find("returncode").text

                    if return_code == "SUCCESS":
                        self.logger.info("Webhook registered successfuly to '{}'".format(self._server))
                        print("Webhook registered successfuly to '{}'".format(self._server))
                    else:
                        self.logger.warn("Webhook failed to register to '{}'".format(self._server))
                        print("Webhook failed to register to '{}'".format(self._server))
                else:
                    self.logger.warn("Webhook failed to register to '{}'".format(self._server))
                    print("Webhook failed to register to '{}'".format(self._server))

                    raise HookCreateError()

            return r

        def _build_create_hook_url(self):
            return urljoin(self._server, "bigbluebutton/api/hooks/create")

    def __init__(self, servers, callback_url, get_raw=False, hook_id=None):
        self._servers = servers
        self._callback_url = callback_url
        self._get_raw = get_raw
        self._hook_id = hook_id
        self._success_servers = []
        self._failed_servers = []

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
            inner_server = self.Server(server, token)
            try:
                _ = inner_server.create_hook(self._callback_url, self._get_raw, self._hook_id)
            except HookCreateError as err:
                self.failed_servers.append(server)
            else:
                self.success_servers.append(server)


class HookCreateError(Exception):
    pass
