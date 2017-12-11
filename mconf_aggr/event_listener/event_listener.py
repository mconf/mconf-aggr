#!/usr/bin/env python3.6

import json
import logging
import time
from urllib.parse import unquote

import falcon

import mconf_aggr.cfg as cfg
from mconf_aggr.aggregator import Aggregator, SetupError, PublishError
from mconf_aggr.event_listener import db_mapping
from mconf_aggr.event_listener.db_operations import DataWritter
from mconf_aggr.utils import time_logger


# Falcon follows the REST architectural style, meaning (among
# other things) that you think in terms of resources and state
# transitions, which map to HTTP verbs.
class HookListener(object):
    def __init__(self, data_handler, logger=None):
        self.data_handler = data_handler
        self.logger = logger or logging.getLogger(__name__)

    def on_post(self, req, resp):
        """Handles POST requests
        """
        self.logger.info("Message from Webhooks received.")
        with time_logger(self.logger.debug,
                         "Processing webhook took {elapsed}s."):
            # Parse received message
            post_data = req.stream.read().decode('utf-8')

            self.data_handler.process_data(post_data)

            resp.status = falcon.HTTP_200  # This is the default status


class AuthMiddleware(object):
    def process_request(self,req,resp):
        """Process the request before routing it.

        Parameters
        ----------
        req : falcon.request.Request
            Request object that will eventually be
            routed to an on_* responder method.
        resp : falcon.request.Response
            Response object that will be routed to
            the on_* responder.
        """
        token = req.get_header('Authorization')
        challenges = ['Token type="Bearer"']

        if token is None:
            description = ('Please provide an auth token '
                           'as part of the request.')

            raise falcon.HTTPUnauthorized('Auth token required',
                                          description,
                                          challenges,
                                          href='http://docs.example.com/auth')

        if not self._token_is_valid(token):
            description = ('The provided auth token is not valid. '
                           'Please request a new token and try again.')

            raise falcon.HTTPUnauthorized('Authentication required',
                                          description,
                                          challenges,
                                          href='http://docs.example.com/auth')

    def _token_is_valid(self, token):
        expected = 'Bearer ' + cfg.config['event_listener']['auth']['token']

        if(expected == token):
            return True
        else:
            return False


class DataHandler():

    def __init__(self, publisher, channel, logger=None):
        self.publisher = publisher
        self.channel = channel
        self.logger = logger or logging.getLogger(__name__)

    def stop(self):
        # stop falcon?
        pass

    def process_data(self, data):
        decoded_data = unquote(data)
        posted_obj = json.loads(decoded_data)

        for webhook_msg in posted_obj:
            # Map message
            mapped_msg = db_mapping.map_message_to_db(webhook_msg)

            if(mapped_msg):
                try:
                    data = [webhook_msg, mapped_msg]
                    self.publisher.publish(data, channel=self.channel)
                except PublishError as err:
                    self.logger.error("Something went wrong while publishing.")
                    continue
