"""This module is responsible for treating HTTP POSTs

It will receive, validate, parse and send the parsed data to an Aggregator thread,
which will properly manipulate the data.

"""
import json
import logging
import time
from urllib.parse import unquote

import falcon

import mconf_aggr.aggregator.cfg as cfg
from mconf_aggr.aggregator.aggregator import Aggregator, SetupError, PublishError
from mconf_aggr.aggregator.utils import time_logger
from mconf_aggr.webhook.db_operations import WebhookDataWriter
from mconf_aggr.webhook.event_mapper import map_webhook_event
from mconf_aggr.webhook.exceptions import WebhookError, RequestProcessingError


"""Falcon follows the REST architectural style, meaning (among
other things) that you think in terms of resources and state
transitions, which map to HTTP verbs.
"""

class HookListener:
    """Listener for webhooks.

    This class is passed to falcon_API to handle requests made to it, this class might have
    more methods if needed, on the format on_*. It could treat POST,GET,PUT and DELETE requests.
    """
    def __init__(self, data_handler, logger=None):
        """Constructor of the HookListener

        Parameters
        ----------
        data_handler : WebhookDataHandler.
        logger : logging.Logger
            If not supplied, it will instantiate a new logger from __name__.
        """
        self.data_handler = data_handler
        self.logger = logger or logging.getLogger(__name__)

    def on_post(self, req, resp):
        """Handles POST requests.

        After receiving a POST call the data_handler to treat the received message.
        """
        # Parse received message
        self.logger.info("Webhook event received from '{}'.".format(req.host))
        with time_logger(self.logger.debug,
                         "Processing webhook event took {elapsed}s."):
            server_url = req.get_param("domain")
            event = req.get_param("event")

            try:
                self.data_handler.process_data(server_url, event)
            except WebhookError as err:
                resp.body = json.dumps({"message": str(err)})
                resp.status = falcon.HTTP_400
            else:
                resp.body = json.dumps({"message": "event processed successfully"})
                resp.status = falcon.HTTP_200  # This is the default status


class AuthMiddleware:
    """Middleware used for authentication.

    This class is used directly by falcon to authenticate incoming events.
    """
    def process_request(self, req, resp):
        """Process the request before routing it.

        It follows the RFC 7235 (https://tools.ietf.org/html/rfc7235)
        and general guidelines provided by
        http://self-issued.info/docs/draft-ietf-oauth-v2-bearer.html
        and
        https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/WWW-Authenticate

        Parameters
        ----------
        req : falcon.request.Request
            Request object that will eventually be
            routed to an on_* responder method.
        resp : falcon.request.Response
            Response object that will be routed to
            the on_* responder.
        """
        self.logger = logging.getLogger(__name__)

        auth_required = cfg.config['webhook']['auth']['required']

        if auth_required:
            requester = req.host # It may not be the original requester.
            token = req.get_header('Authorization')
            www_authentication = ["Bearer realm=\"mconf-aggregator\""]


            if token is None:
                self.logger.warn(
                    "Authentication token missing from '{}'.".format(requester)
                )
                raise falcon.HTTPUnauthorized(
                    "Authentication required",
                    "Provide an authentication token as part of the request",
                    www_authentication
                )

            if not self._token_is_valid(token):
                self.logger.warn(
                    "Invalid token '{}' from '{}'.".format(token, requester)
                )
                raise falcon.HTTPUnauthorized(
                    "Invalid authentication token",
                    "The provided authentication token is not valid",
                    www_authentication
                )

    def _token_is_valid(self, token):
        expected = 'Bearer ' + cfg.config['webhook']['auth']['token']

        if(expected == token):
            return True
        else:
            return False


class WebhookDataHandler:
    """Handler of data from webhooks.

    This class is responsible for publishing the data to Aggregator to create a new thread
    and instantiate the proper WebhookDataWriter.

    It's called by the HookListener everytime it gets a new message.
    """
    def __init__(self, publisher, channel, logger=None):
        """Constructor of WebhookDataHandler.

        Parameters
        ----------
        publisher : aggregator.Publisher
        channel : str
            Channel where data will be published.
        logger : logging.Logger
            If not supplied, it will instantiate a new logger from __name__.
        """
        self.publisher = publisher
        self.channel = channel
        self.logger = logger or logging.getLogger(__name__)

    def stop(self):
        # stop falcon?
        pass

    def process_data(self, server_url, data):
        """Parse and publish data to aggregator.

        Parameters
        ----------
        server_url : str
            event origin's URL.
        data : str
            data to be parsed and published.
        """
        decoded_data = unquote(data)

        try:
            posted_obj = json.loads(decoded_data)
        except json.JSONDecodeError as err:
            self.logger.error("Error during data decoding: invalid JSON.")
            raise RequestProcessingError("data provided is not a valid JSON")


        for webhook_event in posted_obj:
            webhook_event["server_url"] = server_url
            try:
                mapped_event = map_webhook_event(webhook_event)
            except Exception as err:
                mapped_event = None
                raise err

            if(mapped_event):
                try:
                    data = [webhook_event, mapped_event]
                    self.publisher.publish(data, channel=self.channel)
                except PublishError as err:
                    self.logger.error("Something went wrong while publishing.")
                    continue
