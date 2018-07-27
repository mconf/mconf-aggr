#!/usr/bin/env python3.6

import json
import logging
import time
import sys
from urllib.parse import unquote

import falcon

import mconf_aggr.aggregator.cfg as cfg
from mconf_aggr.webhook import db_mapping
from mconf_aggr.webhook.db_operations import DataWritter
from mconf_aggr.webhook.event_listener import DataHandler, HookListener, AuthMiddleware
from mconf_aggr.aggregator.aggregator import Aggregator, SetupError, PublishError

cfg.config.setup_config("config/config.json")
cfg.config.setup_logging()
route = cfg.config['webhook']['route']
logger = logging.getLogger(__name__)

# falcon.API instances are callable WSGI apps
app = falcon.API(middleware=AuthMiddleware())

channel = "webhooks"
db_writter = DataWritter()

aggregator = Aggregator()
aggregator.register_callback(db_writter, channel=channel)

try:
    aggregator.setup()
except SetupError:
    sys.exit(1)

publisher = aggregator.publisher

data_handler = DataHandler(publisher, channel)
hook = HookListener(data_handler)
app.add_route(route, hook)

aggregator.start()
# when?
#aggregator.stop()
#db_reader.stop()

# hook will handle all requests to the self.route URL path
