import requests
import urllib.parse
import json

from datetime import datetime
from config import Config

cfg = Config()

def timestamp_now():
    return int(datetime.timestamp(datetime.now()) * 1000)

def post_event(event, url=cfg.url_endpoint, domain=cfg.domain, header=cfg.header):
    if not isinstance(event, list):
        event = [event]
        
    data = {
        "domain": domain,
        "event": json.dumps(event),
        "timestamp": timestamp_now()
    }

    requests.post(url=url, data=urllib.parse.urlencode(data), headers=header)
