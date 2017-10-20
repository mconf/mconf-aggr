import json

import falcon

import db_operations
import db_mapping

# Falcon follows the REST architectural style, meaning (among
# other things) that you think in terms of resources and state
# transitions, which map to HTTP verbs.
class HookListener(object):
    def on_post(self, req, resp):
        # TODO: Treat when receiving multiple events on POST
        """Handles POST requests"""
        # Parse received message
        post_data = req.stream.read()
        posted_obj = json.loads(post_data)
        # Map message
        mapped_msg = db_mapping.map_message_to_db(posted_obj)
        # Update DB
        db_operations.db_event_selector(posted_obj,mapped_msg)

        resp.status = falcon.HTTP_200  # This is the default status

# falcon.API instances are callable WSGI apps
app = falcon.API()

# Resources are represented by long-lived class instances
hook = HookListener()

# hook will handle all requests to the '/' URL path
app.add_route('/', hook)
