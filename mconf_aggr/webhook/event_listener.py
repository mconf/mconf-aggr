"""This module is responsible for treating HTTP requests.

It will receive, validate, parse and send the parsed data to be processed.
"""
import json
import logging

import falcon

import mconf_aggr.aggregator.cfg as cfg
from mconf_aggr.aggregator.aggregator import PublishError
from mconf_aggr.aggregator.utils import RequestTimeLogger, time_logger
from mconf_aggr.logger import get_logger
from mconf_aggr.webhook.database_handler import AuthenticationHandler
from mconf_aggr.webhook.event_mapper import map_webhook_event
from mconf_aggr.webhook.exceptions import RequestProcessingError, WebhookError

"""Falcon follows the REST architectural style, meaning (among
other things) that you think in terms of resources and state
transitions, which map to HTTP verbs.
"""


class AuthMiddleware:
    """Middleware used for authentication.

    This class is used directly by Falcon to authenticate incoming events.
    It is used before the request is handled.
    """

    def __call__(self, req, resp, resource, params):
        """Make this class callable.

        It enables the class to be set in falcon.before and be used
        like a middleware. It currently drops the resource and params arguments.
        """
        self.process_request(req, resp)

    def process_request(self, req, resp):
        """Process the request before routing it.

        If the request is in any way invalid, raise an error. Otherwise, it returns
        normally.

        Parameters
        ----------
        req : falcon.Request
            Request object that will eventually be routed to an on_* responder method.
        resp : falcon.Response
            Response object that will be routed to the on_* responder.

        Raises
        ------
        falcon.HTTPUnauthorized
            If request authentication fails.

        References
        ----------
        * https://tools.ietf.org/html/rfc7235
        * http://self-issued.info/docs/draft-ietf-oauth-v2-bearer.html
        * https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/WWW-Authenticate
        """
        self.logger = get_logger()

        self.logger.info(f"Received request: '{req.params}'")

        auth_required = cfg.config["MCONF_WEBHOOK_AUTH_REQUIRED"]

        if auth_required:
            server_url = req.get_param("domain")

            if not server_url:
                self.logger.warning(
                    "Domain missing from (last hop) '{}'.".format(req.host)
                )
                raise falcon.HTTPUnauthorized(
                    title="Domain required for authentication",
                    description="Provide a valid domain as part of the request",
                )

            server_url = _normalize_server_url(server_url)
            token = req.get_header("Authorization")
            www_authentication = {"Bearer realm": '"mconf-aggregator"'}

            if token is None:
                self.logger.warning(
                    "Authentication token missing from '{}'.".format(server_url)
                )
                raise falcon.HTTPUnauthorized(
                    title="Authentication required",
                    description="Provide an authentication token as part of the "
                    "request",
                    headers=www_authentication,
                )

            if not self._token_is_valid(server_url, token):
                requester = req.host
                self.logger.warning(
                    "Unable to validate token '{}' from '{}' (last hop: '{}').".format(
                        token, server_url, requester
                    )
                )
                raise falcon.HTTPUnauthorized(
                    title="Unable to validate authentication token",
                    description="The provided authentication token could not be "
                    "validate",
                    headers=www_authentication,
                )

    def _token_is_valid(self, host, token, handler=None):
        """Return True if it can find a token for the given host and
        the token found, when prefixed with an authentication preamble (Bearer),
        matches exactly the token received. Otherwise, it returns False.
        """
        if not handler:
            handler = AuthenticationHandler()

        secret = handler.secret(host)

        if secret:
            expected = "Bearer " + secret

            if expected == token:
                return True

        return False


class WebhookEventListener:
    """Listener for webhooks.

    This class is passed to falcon.API to handle requests made to itself.
    This class might have more methods if needed, on the format on_*.
    It could handle POST, GET, PUT and DELETE requests as well.
    """

    def __init__(self, event_handler, logger=None):
        """Constructor of the WebhookEventListener.

        Parameters
        ----------
        event_handler : WebhookEventHandler.
        logger : loguru.Logger
            If not supplied, it will instantiate a new logger.
        """
        self.event_handler = event_handler
        self.logger = logger or get_logger()

    @falcon.before(AuthMiddleware())
    def on_post(self, req, resp):
        """Handle POST requests.

        After receiving a POST call the event_handler to handle the received message.

        Parameters
        ----------
        req : falcon.Request
        resp : falcon.Response
        """
        with RequestTimeLogger.time_logger_requests(
            self.logger.info,
            "Processing webhook event took {elapsed}s.",
        ):
            server_url = req.get_param("domain")
            event = req.get_param("event")

            self.logger.info(
                "Webhook event received from '{}' (last hop: '{}').".format(
                    server_url, req.host
                )
            )

            # Always responds with HTTP status code 200 in order to prevent
            # the sending webhook endpoint from stopping requesting.
            try:
                self.logger.debug("Processing event")
                self.event_handler.process_event(server_url, event)
            except WebhookError as err:
                self.logger.error(f"An error occurred while processing event: {err}")
                response = WebhookResponse(str(err))
                resp.text = json.dumps(response.error)
                resp.status = falcon.HTTP_200
            except Exception as err:
                self.logger.error(
                    f"An unexpected error occurred while processing event: {err}"
                )
                response = WebhookResponse(str(err))
                resp.text = json.dumps(response.error)
                resp.status = falcon.HTTP_200
            else:
                response = WebhookResponse("Event processed successfully")
                resp.text = json.dumps(response.success)
                resp.status = falcon.HTTP_200


class WebhookResponse:
    """Basic response.

    This class represents the basic format of a response provided by the
    webhook listener. It can be extended to fullfil future needs and extensions
    of the webhook listener API.
    """

    def __init__(self, message):
        """Constructor of the WebhookResponse.

        Parameters
        ----------
        message : str
            Message to be sent back to the requester.
        """
        self.message = message

    @property
    def success(self):
        return self._response("Success")

    @property
    def error(self):
        return self._response("Error")

    def _response(self, status):
        return {"status": status, "message": self.message}


class WebhookEventHandler:
    """Handler of events from webhooks.

    This class is responsible for publishing the data to Aggregator to create
    a new thread and instantiate the proper WebhookDataWriter.

    It's called by the WebhookvEventListener everytime it gets a new message.
    """

    def __init__(self, publisher, channel, logger=None):
        """Constructor of WebhookEventHandler.

        Parameters
        ----------
        publisher : aggregator.Publisher
        channel : str
            Channel where event will be published.
        logger : loguru.Logger
            If not supplied, it will instantiate a new logger.
        """
        self.publisher = publisher
        self.channel = channel
        self.logger = logger or get_logger()

    def stop(self):
        pass

    def process_event(self, server_url, event):
        """Parse and publish data to aggregator.

        Raises
        Exception
            If any error occur during event handling.

        Parameters
        ----------
        server_url : str
            event origin's URL.
        event : str
            event to be parsed and published.
        """

        # TODO(psv): verify if this is essential
        # unquoted_event = unquote(event)

        try:
            # decoded_events = self._decode(unquoted_event)
            self.logger.debug("Parsing events as a JSON file.")
            decoded_events = self._decode(event)
        except json.JSONDecodeError as err:
            self.logger.error(f"Error during event decoding: invalid JSON: {err}")
            raise RequestProcessingError("Event provided is not a valid JSON")

        if server_url:
            # In case the server URL does not contain a valid scheme.
            self.logger.debug("Normalizing server url.")

            server_url = _normalize_server_url(server_url)

        deprecated_events = cfg.config["MCONF_WEBHOOK_DEPRECATED_EVENTS"]

        # We can handle more than one event at once.
        for webhook_event in decoded_events:
            with time_logger(self.logger.info, "Handling event took {elapsed}s."):
                webhook_event["server_url"] = server_url
                try:
                    # Instance of WebhookEvent.
                    webhook_event = map_webhook_event(webhook_event)

                except Exception as err:
                    self.logger.warning(f"Something went wrong: {err}")
                    webhook_event = None

                if webhook_event:
                    if webhook_event.event_type in deprecated_events:
                        self.logger.info(
                            "Received event is in deprecated event list: '{}'".format(
                                deprecated_events
                            )
                        )

                    else:
                        try:
                            self.logger.debug("Publishing event.")
                            self.publisher.publish(webhook_event, channel=self.channel)

                        except PublishError:
                            self.logger.error("Something went wrong while publishing.")
                            continue

                else:
                    self.logger.warning(
                        "Not publishing event from '{}'".format(server_url)
                    )

    def _decode(self, event):
        return json.loads(event)


def _normalize_server_url(server_url):
    """Naive approach for sanitizing URLs."""
    server_url = server_url.strip()

    if not server_url.startswith(("http://", "https://")):
        # HTTPS is the default scheme.
        server_url = "https://" + server_url

    return server_url
