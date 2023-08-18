import json
import urllib.parse
from datetime import datetime
from pprint import pprint

import requests
from config import Config

cfg = Config()


def timestamp_now():
    return int(datetime.timestamp(datetime.now()) * 1000)


def post_event(event, url=cfg.url_endpoint, domain=cfg.domain, header=cfg.header):
    if not isinstance(event, list):
        event = [event]

    data = {"domain": domain, "event": json.dumps(event), "timestamp": timestamp_now()}

    event_data = event[0]["data"]
    print(f"Sending event -> {event_data['id']}")
    for k, v in event_data["attributes"].items():
        print(f"{k}: {v}")
    print()

    requests.post(url=url, data=urllib.parse.urlencode(data), headers=header)
