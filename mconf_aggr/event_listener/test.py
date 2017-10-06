import falcon
import db as DB
import json
import DBMapping

# Falcon follows the REST architectural style, meaning (among
# other things) that you think in terms of resources and state
# transitions, which map to HTTP verbs.
class HookListener(object):
    def on_post(self, req, resp):
        """Handles POST requests"""

        postData = req.stream.read()
        postedObj = json.loads(postData)

        mappedMsg = DBMapping.mapMessageToDB(postedObj)
        DB.dbEventSelector(postedObj,mappedMsg)


        # TODO: MAP RECEIVED MESSAGE TO INTERNAL OBJ
        # TODO: Check which DB event to call
        # TODO: Test with webhooks app
        # TODO: See proper structure
        # TODO: Set to work together with aggr app
        resp.status = falcon.HTTP_200  # This is the default status

# falcon.API instances are callable WSGI apps
app = falcon.API()

# Resources are represented by long-lived class instances
hook = HookListener()

# hook will handle all requests to the '/' URL path
app.add_route('/', hook)
