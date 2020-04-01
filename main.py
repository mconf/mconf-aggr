#!/usr/bin/env python3.6

import json
import logging
import time
import sys
from urllib.parse import unquote

import falcon

import mconf_aggr.aggregator.cfg as cfg
from mconf_aggr.webhook.database import DatabaseConnector
from mconf_aggr.webhook.database_handler import WebhookDataWriter
from mconf_aggr.webhook.event_listener import WebhookEventHandler, WebhookEventListener, AuthMiddleware, KafkaEventListener
from mconf_aggr.webhook.probe_listener import LivenessProbeListener, ReadinessProbeListener
from mconf_aggr.webhook.hook_register import WebhookRegister
from mconf_aggr.aggregator.aggregator import Aggregator, SetupError, PublishError


logger = logging.getLogger(__name__)

# falcon.API instances are callable WSGI apps.
#app = falcon.API(middleware=AuthMiddleware())
app = falcon.API()

# Consume and merge request's contents into params.
req_opt = app.req_options
req_opt.auto_parse_form_urlencoded = True


route = cfg.config["MCONF_WEBHOOK_ROUTE"]

channel = "webhooks"
webhook_writer = WebhookDataWriter()
aggregator = Aggregator()

database = DatabaseConnector()

database.connect()

aggregator.register_callback(webhook_writer, channel=channel)

try:
    aggregator.setup()
except SetupError:
    sys.exit(1)

publisher = aggregator.publisher

event_handler = WebhookEventHandler(publisher, channel)
kafka_listener = KafkaEventListener(event_handler)

app.add_route("/health", LivenessProbeListener())
app.add_route("/ready", ReadinessProbeListener())

should_register = cfg.config["MCONF_WEBHOOK_SHOULD_REGISTER"]
if should_register:
    # Auto-register webhook callback to servers.
    webhook_register = WebhookRegister(
        callback_url=cfg.config["MCONF_WEBHOOK_CALLBACK_URL"]
    )
    webhook_register.create_hooks()

aggregator.start()

database.close()
