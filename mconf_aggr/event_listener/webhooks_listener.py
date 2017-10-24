import json

import falcon

import db_mapping

# Falcon follows the REST architectural style, meaning (among
# other things) that you think in terms of resources and state
# transitions, which map to HTTP verbs.
class HookListener(object):
    def on_post(self, req, resp):
        # TODO: Treat when receiving multiple events on POST
        """Handles POST requests"""
        DataReader.read(req)

        resp.status = falcon.HTTP_200  # This is the default status


class DataReader():

    def __init__(self):
        self.route = cfg.config['route']
        self.hook = HookListener()

    def setup(self, publisher):
        # falcon.API instances are callable WSGI apps
        self.app = falcon.API()
        # hook will handle all requests to the self.route URL path
        self.app.add_route(self.route, self.hook)
        self.publisher = publisher

    def stop(self):
        # stop falcon?

    def read(self, data):
        # TODO: Validade checksum
        # Parse received message
        post_data = data.stream.read()

        # Message will be in format event={data}&timestamp=BigInteger and encoded
        decoded_data = urllib.unquote_plus(post_data)
        decoded_data = decoded_data.split('&')

        # Set {data} in event={data} to events variable
        events = decoded_data[0].split('=',1)[1]
        timestamp = decoded_data[1].split('=',1)[1]

        posted_obj = json.loads(events)
        for webhook_msg in posted_obj:
            # Map message
            mapped_msg = db_mapping.map_message_to_db(webhook_msg)

            if(mapped_msg):
                try:
                    self.publisher.publish(webhook_msg, mapped_msg, channel='name_tbd')
                except PublishError as err:
                    continue
