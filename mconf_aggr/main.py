import gevent

gevent.monkey.patch_all()

import signal
import sys

import falcon

import mconf_aggr.aggregator.cfg as cfg
from mconf_aggr.aggregator.aggregator import Aggregator, SetupError
from mconf_aggr.aggregator.utils import signal_handler
from mconf_aggr.logger import get_logger
from mconf_aggr.webhook.database import DatabaseConnector
from mconf_aggr.webhook.database_handler import WebhookDataWriter
from mconf_aggr.webhook.event_listener import WebhookEventHandler, WebhookEventListener
from mconf_aggr.webhook.hook_register import WebhookRegister
from mconf_aggr.webhook.probe_listener import (
    LivenessProbeListener,
    ReadinessProbeListener,
)

logger = get_logger()

# falcon.API instances are callable WSGI apps.
app = falcon.App()

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

livenessProbe = LivenessProbeListener()
readinessProbe = ReadinessProbeListener()

try:
    aggregator.setup()

    # Create the signal handling for graceful shutdown
    gevent.signal_handler(
        signal.SIGTERM, signal_handler, aggregator, livenessProbe, signal.SIGTERM
    )
except SetupError:
    sys.exit(1)

publisher = aggregator.publisher

event_handler = WebhookEventHandler(publisher, channel)
hook = WebhookEventListener(event_handler)

app.add_route(route, hook)
app.add_route("/health", livenessProbe)
app.add_route("/ready", readinessProbe)

should_register = cfg.config["MCONF_WEBHOOK_SHOULD_REGISTER"]
if should_register:
    # Auto-register webhook callback to servers.
    webhook_register = WebhookRegister(
        callback_url=cfg.config["MCONF_WEBHOOK_CALLBACK_URL"]
    )
    webhook_register.create_hooks()

aggregator.start()

database.close()
