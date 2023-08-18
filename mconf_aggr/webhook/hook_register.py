import hashlib
import json
import logging
import urllib.parse
from urllib.parse import urljoin
from xml.etree import ElementTree

import requests

from mconf_aggr.logger import get_logger
from mconf_aggr.webhook.database_handler import WebhookServerHandler
from mconf_aggr.webhook.exceptions import DatabaseNotReadyError


class WebhookCreateError(Exception):
    """Raised if any error occur during webhook callback registration."""

    def __init__(self, reason="unexpected reason"):
        self.reason = reason


class WebhookAlreadyExistsError(Exception):
    """Raised if webhook callback registration generated a duplicate."""

    def __init__(self):
        self.reason = "webhook already exists"


class WebhookRegister:
    """Webhook callback register.

    This is class is responsible for registering webhook callbacks.
    """

    def __init__(
        self, callback_url, servers=None, get_raw=False, hook_id=None, logger=None
    ):
        """Constructor of the WebhookRegister.

        Parameters
        ----------
        callback_url : str
            URL of the callback to be registered.
        servers : list
            List of servers to register.
        get_raw : bool
            True if it requests raw webhooks to be received. False otherwise.
        hook_id : int
            Specify a hook ID.
        logger : loguru.Logger
            If not supplied, it will instantiate a new logger.
        """
        self._callback_url = callback_url
        self._get_raw = get_raw
        self._hook_id = hook_id
        self._success_servers = []  # List of servers registered successfully.
        self._failed_servers = []  # List of servers that failed to register.

        self.logger = logger or get_logger()

        if servers:
            # Use the servers passed as argument.
            self._servers = servers
        else:
            # Otherwise, fetch a server list to be used from database.
            self._fetch_servers_from_database()

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
        self.logger.info("Creating hooks.")
        # Iterate over its dictionary of server_name-server_secret key-values.
        # We still use token and secret interchangeably.
        for server, token in self._servers.items():
            inner_server = WebhookServer(server, token)

            # When creating a hook, i.e., registerting a webhook callback,
            # it may fail due to many different reasons.
            # If it fails, appends the failed server to the failed_servers list.
            # Otherwise, the server is good to go on the success_servers list.
            try:
                _ = inner_server.create_hook(
                    self._callback_url, self._get_raw, self._hook_id
                )
            except WebhookCreateError as err:
                self.logger.warning(
                    f"Webhook registration for server '{server}' failed "
                    f"({err.reason})."
                )
                self.failed_servers.append(server)
            except WebhookAlreadyExistsError:
                self.logger.info(
                    f"Webhook registration for server '{server}' ok "
                    "(webhook already exists)."
                )
            except RuntimeError:
                self.logger.warning(
                    f"Webhook registration for server '{server}' failed "
                    "(unexpected reason)."
                )

                self.failed_servers.append(server)
            else:
                self.logger.info(f"Webhook registration for server '{server}' ok.")

                self.success_servers.append(server)

        self.logger.info("Hooks registration done.")

    def _fetch_servers_from_database(self):
        handler = WebhookServerHandler()

        try:
            servers = handler.servers()
        except DatabaseNotReadyError:
            # If any known or unknown error occurred in the database,
            # create an empty dict.
            self._servers = dict()
        else:
            # Otherwise, put the servers in a server_name-server_secret dictionary.
            self._servers = {}
            for server in servers:
                self._servers[server.name] = server.secret


class WebhookServer:
    """A single server to register webhook callback."""

    def __init__(self, server, secret, logger=None):
        """Constructor of `WebhookServer`.

        Parameters
        ----------
        server : str
            Hostname of the server.
        secret : str
            Shared secret (token) of the server.
        logger : loguru.Logger
            If not supplied, it will instantiate a new logger.
        """
        self._server = server
        self._secret = secret

        self.logger = logger or get_logger()

    def create_hook(self, callback_url, get_raw=False, hook_id=None):
        """Register a webhook callback.

        It creates a hooks/create request and sends it to this server.

        Parameters
        ----------
        callback_url : str
            URL of the callback to be registered.
        get_raw : bool
            True if it requests raw webhooks to be received. False otherwise.
        hook_id : int
            Specify a hook ID.

        Raises
        ------
        WebhookCreateError
            If any error occur during webhook callback registration.
        """

        hook_url = self._build_create_hook_url()
        params = {"callbackURL": callback_url, "getRaw": get_raw}
        if hook_id:
            params["hookID"] = hook_id

        params["checksum"] = checksum(
            "hooks/create", urllib.parse.urlencode(params), self._secret
        )

        r = None
        try:
            r = requests.get(hook_url, params=params)
            self.logger.debug(f"response from '{hook_url}': '{r.text}'.")
        except requests.exceptions.ConnectionError as err:
            raise WebhookCreateError("connection error") from err
        except Exception as err:
            # Unexpected error.
            raise WebhookCreateError(str(err)) from err
        else:
            # If it succeeds in getting a response.
            try:
                parse_response(r)

                return r
            except (WebhookCreateError, WebhookAlreadyExistsError) as err:
                # Pass-through the known errors.
                raise err
            except RuntimeError:
                # If it is an unexpected error, raises a generic webhook creation error.
                raise WebhookCreateError()

    def _build_create_hook_url(self):
        """Append the correct resource path of hooks/create to the server URL.

        Returns
        -------
        str
            Server URL with hooks/create resource path appended.
        """
        return urljoin(self._server, "bigbluebutton/api/hooks/create")


def checksum(method, params, secret):
    """Calculate the checksum.

    Parameters
    ----------
    method : str
        Base resource path of the request.
    params : str
        Parameters in urlencoded format.
    secret : str
        Shared secret to append.

    Returns
    -------
    str
        SHA-1 of the string resulting of the concatenation of method, params and
        shared secret provided.
    """
    # We need to make sure the strings are encoded as UTF-8 before calculating the
    # SHA-1.
    encoded_payload = (
        method.encode("utf-8") + params.encode("utf-8") + secret.encode("utf-8")
    )
    sha1_payload = hashlib.sha1(encoded_payload)

    # Converts and returns SHA-1 as str.
    return sha1_payload.hexdigest()


def parse_response(response):
    """Parse the response obtained seeking for any error

    If no error is signaled by the response received, then this method returns
    normally - without raising an exception.

    Parameters
    ----------
    response : falcon.Response

    Raises
    ------
    WebhookAlreadyExistsError
        If the webhook callback has already been registered in the server.
    WebhookCreateError
        If any other error occur. The specific reason is provided as parameter.
    """
    # If it received a HTTP 200 OK as response's status code.
    if response.status_code == requests.codes.ok:
        try:
            # Try to parse response's body as XML.
            response_xml = ElementTree.fromstring(response.text)
        except Exception as err:
            raise WebhookCreateError() from err
        else:
            # If it succeeds in parsing response's body as XML.

            # Try to find returncode and messageKey nodes within the XML.
            # If it can not find it, assign None to these variables.
            return_code_node = response_xml.find("returncode")
            message_key_node = response_xml.find("messageKey")
            return_code = (
                return_code_node.text if return_code_node is not None else None
            )
            message_key = (
                message_key_node.text if message_key_node is not None else None
            )

            # Below is a list of the possible errors that can occur when registering
            # a webhook callback.
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
        # If is did not receive a HTTP 200 OK.
        raise WebhookCreateError(f"status code: {response.status_code}")
