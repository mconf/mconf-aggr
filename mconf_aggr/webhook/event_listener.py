"""This module is responsible for treating HTTP requests.

It will receive, validate, parse and send the parsed data to be processed.
"""
import json
import logging
import time
from urllib.parse import unquote

import falcon
import threading
from kafka import KafkaConsumer

import mconf_aggr.aggregator.cfg as cfg
from mconf_aggr.aggregator.aggregator import Aggregator, SetupError, PublishError
from mconf_aggr.aggregator.utils import time_logger
from mconf_aggr.webhook.database_handler import WebhookDataWriter, AuthenticationHandler
from mconf_aggr.webhook.event_mapper import map_webhook_event
from mconf_aggr.webhook.exceptions import WebhookError, RequestProcessingError


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
        self.logger = logging.getLogger(__name__)

        auth_required = cfg.config["MCONF_WEBHOOK_AUTH_REQUIRED"]

        if auth_required:
            server_url = req.get_param("domain")

            if not server_url:
                self.logger.warn(
                    "Domain missing from (last hop) '{}'.".format(req.host)
                )
                raise falcon.HTTPUnauthorized(
                    "Domain required for authentication",
                    "Provide a valid domain as part of the request"
                )

            server_url = _normalize_server_url(server_url)
            token = req.get_header("Authorization")
            www_authentication = ["Bearer realm=\"mconf-aggregator\""]

            if token is None:
                self.logger.warn(
                    "Authentication token missing from '{}'.".format(server_url)
                )
                raise falcon.HTTPUnauthorized(
                    "Authentication required",
                    "Provide an authentication token as part of the request",
                    www_authentication
                )

            if not self._token_is_valid(server_url, token):
                requester = req.host
                self.logger.warn(
                    "Unable to validate token '{}' from '{}' (last hop: '{}').".format(token, server_url, requester)
                )
                raise falcon.HTTPUnauthorized(
                    "Unable to validate authentication token",
                    "The provided authentication token could not be validate",
                    www_authentication
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
            expected = 'Bearer ' + secret

            if(expected == token):
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
        logger : logging.Logger
            If not supplied, it will instantiate a new logger from __name__.
        """
        self.event_handler = event_handler
        self.logger = logger or logging.getLogger(__name__)

    @falcon.before(AuthMiddleware())
    def on_post(self, req, resp):
        """Handle POST requests.

        After receiving a POST call the event_handler to handle the received message.

        Parameters
        ----------
        req : falcon.Request
        resp : falcon.Response
        """
        with time_logger(self.logger.debug,
                         "Processing webhook event took {elapsed}s."):
            server_url = req.get_param("domain")
            event = req.get_param("event")

            self.logger.info("Webhook event received from '{}' (last hop: '{}').".format(server_url, req.host))

            # Always responds with HTTP status code 200 in order to prevent
            # the sending webhook endpoint from stopping requesting.
            try:
                self.event_handler.process_event(server_url, event)
            except WebhookError as err:
                self.logger.error("An error occurred while processing event.")
                response = WebhookResponse(str(err))
                resp.body = json.dumps(response.error)
                resp.status = falcon.HTTP_200
            except Exception as err:
                self.logger.error("An unexpected error occurred while processing event.")
                response = WebhookResponse(str(err))
                resp.body = json.dumps(response.error)
                resp.status = falcon.HTTP_200
            else:
                response = WebhookResponse("Event processed successfully")
                resp.body = json.dumps(response.success)
                resp.status = falcon.HTTP_200

class KafkaEventListener(threading.Thread):
    """Listener for Kafka.

    This class works as a KafkaConsumer, using a specific thread to run it.
    """

    def __init__(self, event_handler, logger=None, **kwargs):
        """Constructor of the KafkaEventListener.

        Parameters
        ----------
        event_handler : WebhookEventHandler.
        logger : logging.Logger
            If not supplied, it will instantiate a new logger from __name__.
        """
        threading.Thread.__init__(self, **kwargs)
        self.event_handler = event_handler
        self.kafka_host = cfg.config["MCONF_KAFKA_HOST"]
        self.kafka_topic = cfg.config["MCONF_KAFKA_TOPIC"]
        self.kafka_consumer = KafkaConsumer(self.kafka_topic, 
            bootstrap_servers = self.kafka_host, 
            enable_auto_commit=False, group_id=cfg.config["MCONF_KAFKA_GROUP_ID"],
            security_protocol=cfg.config["MCONF_KAFKA_SECURITY_PROTOCOL"],
            sasl_mechanism=cfg.config["MCONF_KAFKA_SASL_MECHANISM"],
            sasl_plain_username=cfg.config["MCONF_KAFKA_SASL_USERNAME"],
            sasl_plain_password=cfg.config["MCONF_KAFKA_SASL_PASSWORD"])
        self.logger = logger or logging.getLogger(__name__)

        self.start()

    def run(self):
        """Method which will run when the thread starts.
        Consuming every message from Kafka and processing it as an event.
        """
        interval = 5
        while True:
            try:
                for message in self.kafka_consumer:
                    with time_logger(self.logger.info,
                                    "Processing webhook event took {elapsed}s."):
                        try:
                            self.event_handler.process_data(message.value)
                        except Exception as err:
                            self.logger.error(f"An unexpected error occurred while processing event ({err}).")

                        self.kafka_consumer.commit()
            except Exception as err:
                self.logger.error(f"An unexpected error occurred while processing event ({err}). Reconnecting to kafka in {interval} seconds.")

                time.sleep(interval)
                
                continue

            


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
        logger : logging.Logger
            If not supplied, it will instantiate a new logger from __name__.
        """
        self.publisher = publisher
        self.channel = channel
        self.logger = logger or logging.getLogger(__name__)

    def stop(self):
        pass

    def process_data(self, data):
        """Parse and publish data to aggregator.

        Raises
        Exception
            If any error occur during event handling.

        Parameters
        ----------
        data : str
            all the data about the event to be parsed and published.
        """
        try:
            decoded_data = self._decode(data)
            server_url = decoded_data["server_domain"]
        except json.JSONDecodeError as err:
            self.logger.error(f"Error during event decoding: invalid JSON: {err}")
            raise RequestProcessingError("Event provided is not a valid JSON")
        except KeyError as err:
            self.logger.error(f"Invalid key in the given event: {err}")
            raise RequestProcessingError("Event provided is not a valid JSON")

        self.logger.info("Event received from '{}'.".format(server_url))

        self.process_event(server_url, [decoded_data], decoded=True)
    
    def process_event(self, server_url, event, decoded=False):
        """Parse and publish data to aggregator.

        Raises
        Exception
            If any error occur during event handling.

        Parameters
        ----------
        server_url : str
            event origin's URL.
        event : str / dict
            event to be parsed and published.
        decoded : boolean
            if true, event is already decoded and it's a dict.
        """
        # TODO(psv): verify if this is essential
        # unquoted_event = unquote(event)

        if not decoded:
            try:
                #decoded_events = self._decode(unquoted_event)
                decoded_events = self._decode(event)
            except json.JSONDecodeError as err:
                self.logger.error(f"Error during event decoding: invalid JSON: {err}")
                raise RequestProcessingError("Event provided is not a valid JSON")
        else:
            decoded_events = event

        if server_url:
            # In case the server URL does not contain a valid scheme.
            server_url = _normalize_server_url(server_url)

        # We can handle more than one event at once.
        for webhook_event in decoded_events:
            webhook_event["server_url"] = server_url
            try:
                # Instance of WebhookEvent.
                webhook_event = map_webhook_event(webhook_event)
            except Exception as err:
                webhook_event = None
                
            if webhook_event:
                try:
                    self.publisher.publish(webhook_event, channel=self.channel)
                except PublishError as err:
                    self.logger.error("Something went wrong while publishing.")
                    continue
            else:
                self.logger.warn("Not publishing event from '{}'".format(server_url))

    def _decode(self, event):
        return json.loads(event)

def _normalize_server_url(server_url):
    """ Naive approach for sanitizing URLs."""
    server_url = server_url.strip()

    if not server_url.startswith(("http://", "https://")):
        # HTTPS is the default scheme.
        server_url = "https://" + server_url

    return server_url
