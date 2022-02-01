"""This module is responsible for treating HTTP requests.

It will receive, validate, parse and send the parsed data to be processed.
"""
import json
import logging
import threading
import logaugment
import time
from urllib.parse import unquote

from kafka import KafkaConsumer

import falcon

import mconf_aggr.aggregator.cfg as cfg
from mconf_aggr.aggregator.utils import time_logger, RequestTimeLogger
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
        logaugment.set(self.logger, code="", site="AuthMiddleware", server="", event="", keywords="null")

        logging_extra = {
            "code": "Processing requests",
            "site": "AuthMiddleware.process_request",
            "keywords": ["https", "falcon", "requests", "domain"]
        }

        self.logger.info(f"Received request: '{req.params}'", extra=dict(logging_extra, keywords=json.dumps(logging_extra["keywords"])))

        auth_required = cfg.config["MCONF_WEBHOOK_AUTH_REQUIRED"]

        if auth_required:
            server_url = req.get_param("domain")

            if not server_url:
                logging_extra["code"] = "Missing domain"
                logging_extra["keywords"] += ["warning"]
                self.logger.warn(
                    "Domain missing from (last hop) '{}'.".format(req.host),
                    extra=dict(logging_extra, keywords=json.dumps(logging_extra["keywords"]))
                )
                raise falcon.HTTPUnauthorized(
                    "Domain required for authentication",
                    "Provide a valid domain as part of the request"
                )

            server_url = _normalize_server_url(server_url)
            token = req.get_header("Authorization")
            www_authentication = ["Bearer realm=\"mconf-aggregator\""]

            logging_extra["server"] = server_url
            if token is None:
                logging_extra["code"] = "Missing token"
                logging_extra["keywords"] += ["warning"] if("warning" not in logging_extra["keywords"]) else []
                self.logger.warn(
                    "Authentication token missing from '{}'.".format(server_url),
                    extra=dict(logging_extra, keywords=json.dumps(logging_extra["keywords"]))
                )
                raise falcon.HTTPUnauthorized(
                    "Authentication required",
                    "Provide an authentication token as part of the request",
                    www_authentication
                )

            if not self._token_is_valid(server_url, token):
                requester = req.host
                logging_extra["code"] = "Validate token"
                logging_extra["keywords"] += ["warning"] if("warning" not in logging_extra["keywords"]) else []
                self.logger.warn(
                    "Unable to validate token '{}' from '{}' (last hop: '{}').".format(token, server_url, requester),
                    extra=dict(logging_extra, keywords=json.dumps(logging_extra["keywords"]))
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

class KafkaEventConsumer(threading.Thread):
    """Consumer for Kafka messages.

    This class receives messages from Kafka, where this messages contains events.
    """
    def __init__(self, event_handler, server, group, topic, logger=None):
        """Constructor of the KafkaEventConsumer.

        Parameters
        ----------
        event_handler : WebhookEventHandler.
        server : str
            It's the address of the Kafka server which will send the events.
        group : str
            It's the consumer group which this consumer must integrate.
        topic : str
            It's the topic which this consumer will subscribe.
        logger : logging.Logger
            If not supplied, it will instantiate a new logger from __name__.
        """
        super(KafkaEventConsumer, self).__init__()
        self.event_handler = event_handler
        self.consumer = KafkaConsumer(topic, group_id=group, bootstrap_servers=server)
        self.is_running = False
        self.logger = logger or logging.getLogger(__name__)
        logaugment.set(self.logger, code="", site="KafkaEventConsumer", server="", event="", keywords="null")

    def run(self):
        """Wait for event and sends it to event_handler.

        After receiving an event the event_handler to handle the received message.
        """
        self.is_running = True
        logging_extra = {
            "code": "KafkaEventConsumerRun",
            "site": "KafkaEventConsumer.run",
            "keywords": ["kafka", "event", "listener"]
        }

        self.logger.info("KafkaEventConsumer start running", extra=dict(logging_extra, keywords=json.dumps(logging_extra["keywords"])))

        while self.is_running:
            for msg in self.consumer:
                with RequestTimeLogger.time_logger_requests(self.logger.info,
                                "Processing webhook event took {elapsed}s.", extra=dict(logging_extra, keywords=json.dumps(logging_extra["keywords"]))):
                    event = msg.value
                    server_url = dict(msg.headers)["server"].decode('utf-8')
                    try:
                        logging_extra["code"] = "Processing webhook event"
                        self.logger.debug("Processing event", extra=dict(logging_extra, keywords=json.dumps(logging_extra["keywords"])))
                        self.event_handler.process_event(server_url, event)
                    except WebhookError as err:
                        logging_extra["code"] = "Webhook error"
                        logging_extra["keywords"] += ["exception", "error"]
                        self.logger.error(f"An error occurred while processing event: {err}", extra=dict(logging_extra, keywords=json.dumps(logging_extra["keywords"])))
                    except Exception as err:
                        logging_extra["code"] = "Unexpected error"
                        logging_extra["keywords"] += ["exception", "error"]
                        self.logger.error(f"An unexpected error occurred while processing event: {err}", extra=dict(logging_extra, keywords=json.dumps(logging_extra["keywords"])))

    def stop(self):
        """Stops the loop to consume messages from Kafka.
        """
        self.is_running = False
        self.consumer.close()


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


class KafkaEventHandler:
    """Handler of events from Kafka.

    This class is responsible for publishing the data to Aggregator to create
    a new thread and instantiate the proper WebhookDataWriter.

    It's called by the WebhookvEventListener everytime it gets a new message.
    """
    def __init__(self, writer, logger=None):
        """Constructor of WebhookEventHandler.

        Parameters
        ----------
        writer : WebhookDataWriter
            Writer to start hadling the data and persist it into the database.
        logger : logging.Logger
            If not supplied, it will instantiate a new logger from __name__.
        """
        self.writer = writer
        self.logger = logger or logging.getLogger(__name__)
        logaugment.set(self.logger, code="", site="WebhookEventHandler", server="", event="", keywords="null")

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
        logging_extra = {
            "code": "Parse and publish data",
            "site": "WebhookEventHandler.process_event",
            "server": server_url or "",
            "keywords": ["WebhookEventHandler", "parse", "publish", "data", "process", "to aggregator"]
        }

        # TODO(psv): verify if this is essential
        # unquoted_event = unquote(event)

        try:
            #decoded_events = self._decode(unquoted_event)
            logging_extra["code"] = "Decoding events"
            self.logger.debug("Parsing events as a JSON file.", extra=dict(logging_extra, keywords=json.dumps(logging_extra["keywords"])))
            webhook_event = self._decode(event)
        except json.JSONDecodeError as err:
            logging_extra["code"] = "Invalid JSON"
            logging_extra["keywords"] += ["JSON", "error", "except"]
            self.logger.error(f"Error during event decoding: invalid JSON: {err}")
            raise RequestProcessingError("Event provided is not a valid JSON")

        if server_url:
            # In case the server URL does not contain a valid scheme.
            logging_extra["code"] = "Decoding url"
            self.logger.debug("Normalizing server url.", extra=dict(logging_extra, keywords=json.dumps(logging_extra["keywords"])))

            server_url = _normalize_server_url(server_url)

            logging_extra["server"] = server_url

        deprecated_events = cfg.config["MCONF_WEBHOOK_DEPRECATED_EVENTS"]

        # We can handle more than one event at once.
        with time_logger(self.logger.info,
                            "Handling event took {elapsed}s.", extra=dict(logging_extra, keywords=json.dumps(logging_extra["keywords"]))):
            webhook_event["server_url"] = server_url
            try:
                # Instance of WebhookEvent. 
                webhook_event = map_webhook_event(webhook_event)

            except Exception as err:
                logging_extra["code"] = "Mapping error"
                logging_extra["keywords"] += ["mapper", "warning"]
                self.logger.warning(f"Something went wrong: {err}")
                webhook_event = None
            

            if webhook_event:
                if webhook_event.event_type in deprecated_events:
                    logging_extra["code"] = "Event deprecated"
                    logging_extra["event"] = webhook_event.event_type
                    logging_extra["server"] = webhook_event.server_url
                    logging_extra["keywords"] = ["WebhookEventHandler", "parse", "publish", "data", "process", "to aggregator"]
                    self.logger.info("Received event is in deprecated event list: '{}'".format(deprecated_events), extra=dict(logging_extra, keywords=json.dumps(logging_extra["keywords"])))

                else:
                    try:
                        logging_extra["event"] = webhook_event.event_type
                        logging_extra["code"] = "Publishing webhook event"
                        logging_extra["keywords"] = ["WebhookEventHandler", "parse", "publish", "data", "process", "to aggregator"]
                        self.logger.debug("Publishing event.", extra=dict(logging_extra, keywords=json.dumps(logging_extra["keywords"])))
                        self.writer.run(webhook_event)

                    except Exception as err:
                        logging_extra["code"] = "Writing error"
                        logging_extra["keywords"] = ["WebhookEventHandler", "parse", "publish", "data", "process", "to aggregator", "exception", "error"]
                        self.logger.error("Something went wrong while publishing.")
                        raise

            else:
                logging_extra["code"] = "Not publishing"
                logging_extra["keywords"] = ["WebhookEventHandler", "parse", "publish", "data", "process", "to aggregator", "warning"]
                self.logger.warn("Not publishing event from '{}'".format(server_url))

            logging_extra["code"] = "HandlingEventTime"
            logging_extra["keywords"] = ["event", "handle", "time", "map", "publish"]

    def _decode(self, event):
        return json.loads(event)

def _normalize_server_url(server_url):
    """ Naive approach for sanitizing URLs."""
    server_url = server_url.strip()

    if not server_url.startswith(("http://", "https://")):
        # HTTPS is the default scheme.
        server_url = "https://" + server_url

    return server_url
