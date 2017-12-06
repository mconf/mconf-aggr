#!/usr/bin/env python3.6

import json
import logging
import time
from urllib.parse import unquote

import falcon

import mconf_aggr.cfg as cfg
from mconf_aggr.event_listener import db_mapping
from mconf_aggr.event_listener.db_operations import DataWritter
from mconf_aggr.aggregator import Aggregator, SetupError, PublishError



# Falcon follows the REST architectural style, meaning (among
# other things) that you think in terms of resources and state
# transitions, which map to HTTP verbs.
class HookListener(object):
    """Listener for webhooks.

    This class is passed to falcon_API to handle requests made to it, this class might have
    more methods if needed, on the format on_*. It could treat POST,GET,PUT and DELETE requests.
    """
    def __init__(self, data_handler):
        """Constructor of the HookListener

        Parameters
        ----------
        data_handler : Instance of the DataHandler Class.
        """
        self.data_handler = data_handler

    def on_post(self, req, resp):
        """Handles POST requests

        After receiving a POST call the data_handler to treat the received message.
        """
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
    """Handler of data from webhooks.

    This class is responsible for publishing the data to Aggregator to create a new thread
    and instantiate the proper DataWritter.

    It's called by the HookListener everytime it gets a new message.
    """
    def __init__(self, publisher, channel):
        """Constructor of DataHandler.

        Parameters
        ----------
        publisher : Instance of aggregator.publisher .
        channel : str
            Channel where data will be published.
        """
        self.publisher = publisher
        self.channel = channel

    def stop(self):
        # stop falcon?
        pass

    def process_data(self, data):
        """Parse and publish data to aggregator.

        Parameters
        ----------
        data : str
            data to be parsed and published.
        """
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
                    continue
