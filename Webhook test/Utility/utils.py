import requests
import urllib.parse
import json

from datetime import datetime
from config import internal_meeting_id, external_meeting_id, internal_user_id, record_id, url_endpoint, domain, header

def timestamp_now():
    return int(datetime.timestamp(datetime.now()) * 1000)

def post_event(event, url=url_endpoint):
    if not isinstance(event, list):
        event = [event]
        
    data = {
        "domain": domain,
        "event": json.dumps(event),
        "timestamp": timestamp_now()
    }

    requests.post(url=url, data=urllib.parse.urlencode(data), headers=header)