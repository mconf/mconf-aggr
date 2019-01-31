"""This module is responsible for treating HTTP requests.

It will receive, validate, parse and send the parsed data to be processed.
"""
import logging

import falcon


"""Falcon follows the REST architectural style, meaning (among
other things) that you think in terms of resources and state
transitions, which map to HTTP verbs.
"""

class ProbeListener:
    """Listener for Kubernetes probes.

    This class might have more methods if needed, on the format on_*.
    It could handle POST, GET, PUT and DELETE requests as well.
    """
    def __init__(self, logger=None):
        """Constructor of the ProbeListener.

        Parameters
        ----------
        logger : logging.Logger
            If not supplied, it will instantiate a new logger from __name__.
        """
        self.logger = logger or logging.getLogger(__name__)

    def on_get(self, req, resp):
        """Handle GET requests.

        After receiving a GET request a verification method is called to check
        whether it should send back success or failed.

        Parameters
        ----------
        req : falcon.Request
        resp : falcon.Response
        """
        if (self._ok()):
            resp.body = "OK"
            resp.status = falcon.HTTP_200 # OK.
        else:
            resp.body = ""
            resp.status = falcon.HTTP_503 # Service unavailable.

    def _ok(self):
        """This method must be implemented by derived classes.
        """
        raise NotImplementedError()


class LivenessProbeListener(ProbeListener):
    """Listener for the endpoint /health.
    """

    def _ok(self):
        """Implements endpoint-specific logic of /health.

        Returns
        -------
        bool : True if the application is running correctly. False otherwise.
        """
        return True


class ReadinessProbeListener(ProbeListener):
    """Listener for the endpoint /ready.
    """

    def _ok(self):
        """Implements endpoint-specific logic of /health.

        Returns
        -------
        bool : True if the service is ready to handle requests adequately.
        False otherwise.
        """
        return True
