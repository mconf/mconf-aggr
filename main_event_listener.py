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
    def on_post(self, req, resp):
        # TODO: Treat when receiving multiple events on POST
        """Handles POST requests"""
        # Parse received message
        post_data = req.stream.read().decode('utf-8')

        db_reader.read(post_data)

        resp.status = falcon.HTTP_200  # This is the default status


class AuthMiddleware(object):
    def process_request(self,req,resp):
        """Process the request before routing it.

        Args:
            req: Request object that will eventually be
                routed to an on_* responder method.
            resp: Response object that will be routed to
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


class DataReader():

    def __init__(self):
        self.route = cfg.config['event_listener']['route']
        self.hook = HookListener()

    def setup(self, publisher):
        # hook will handle all requests to the self.route URL path
        app.add_route(self.route, self.hook)
        self.publisher = publisher

    def stop(self):
        # stop falcon?
        pass

    def read(self, data):
        # TODO: Validade checksum
        decoded_data = unquote(data)
        posted_obj = json.loads(decoded_data)

        for webhook_msg in posted_obj:
            # Map message
            mapped_msg = db_mapping.map_message_to_db(webhook_msg)

            if(mapped_msg):
                try:
                    data = [webhook_msg, mapped_msg]
                    self.publisher.publish(data, channel='webhooks')
                except PublishError as err:
                    continue


cfg.config.setup_config("config/config.json")

# falcon.API instances are callable WSGI apps
app = falcon.API(middleware=AuthMiddleware())

db_reader = DataReader()
db_writter = DataWritter()

aggregator = Aggregator()
aggregator.register_callback(db_writter, channel='webhooks')

try:
    aggregator.setup()
except SetupError:
    exit(1)

publisher = aggregator.publisher

db_reader.setup(publisher)

# when?
#aggregator.stop()
#db_reader.stop()
