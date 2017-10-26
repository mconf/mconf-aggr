import json
import urllib

import falcon

import db_operations
import db_mapping

# Falcon follows the REST architectural style, meaning (among
# other things) that you think in terms of resources and state
# transitions, which map to HTTP verbs.
class HookListener(object):
    def on_post(self, req, resp):
        """Handles POST requests"""
        # TODO: Validade checksum
        # Parse received message
        post_data = req.stream.read()
        # Message will be in format event={data}&timestamp=BigInteger and encoded
        decoded_data = urllib.unquote_plus(post_data)
        decoded_data = decoded_data.split('&')
        # Set {data} in event={data} to events variable
        events = decoded_data[0].split('=',1)[1]
        timestamp = decoded_data[1].split('=',1)[1]

        posted_obj = json.loads(events)
        for obj in posted_obj:
            # Map message
            mapped_msg = db_mapping.map_message_to_db(obj)

            # Update DB
            db_operations.db_event_selector(obj,mapped_msg)

        resp.status = falcon.HTTP_200  # This is the default status

# falcon.API instances are callable WSGI apps
app = falcon.API()

# Resources are represented by long-lived class instances
hook = HookListener()

# hook will handle all requests to the '/' URL path
# TODO: When setting add_route to Reader.setup, get route from config file
app.add_route('/', hook)
