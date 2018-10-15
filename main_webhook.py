#!/usr/bin/env python3.6

import json
import logging
import time
import sys
from urllib.parse import unquote

import falcon

import mconf_aggr.aggregator.cfg as cfg
from mconf_aggr.webhook.database_handler import WebhookDataWriter
from mconf_aggr.webhook.event_listener import WebhookEventHandler, WebhookEventListener, AuthMiddleware
from mconf_aggr.webhook.hook_register import WebhookRegister
from mconf_aggr.aggregator.aggregator import Aggregator, SetupError, PublishError


# falcon.API instances are callable WSGI apps.
app = falcon.API(middleware=AuthMiddleware())

# Consume and merge request's contents into params.
req_opt = app.req_options
req_opt.auto_parse_form_urlencoded = True

cfg.config.setup_config("config/config.json")
cfg.config.setup_logging()

route = cfg.config['webhook']['route']
logger = logging.getLogger(__name__)

channel = "webhooks"
webhook_writer = WebhookDataWriter()
aggregator = Aggregator()

aggregator.register_callback(webhook_writer, channel=channel)

try:
    aggregator.setup()
except SetupError:
    sys.exit(1)

publisher = aggregator.publisher

event_handler = WebhookEventHandler(publisher, channel)
hook = WebhookEventListener(event_handler)

app.add_route(route, hook)

# Auto-register webhook callback to servers.
webhook_register = WebhookRegister(
    callback_url=cfg.config['webhook']['callback_url']
)
webhook_register.create_hooks()

aggregator.start()
