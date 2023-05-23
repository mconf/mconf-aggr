"""This module is responsible for treating HTTP requests.

It will receive, validate, parse and send the parsed data to be processed.
"""
import json
import logging

import falcon
import sqlalchemy

from mconf_aggr.logger import get_logger
from mconf_aggr.webhook.database import DatabaseConnector
from mconf_aggr.webhook.exceptions import DatabaseNotReadyError

"""Falcon follows the REST architectural style, meaning (among
other things) that you think in terms of resources and state
transitions, which map to HTTP verbs.
"""

session_scope = DatabaseConnector.get_session_scope()


class ProbeListener:
    """Listener for Kubernetes probes.

    This class might have more methods if needed, on the format on_*.
    It could handle POST, GET, PUT and DELETE requests as well.
    """

    def __init__(self, logger=None):
        """Constructor of the ProbeListener.

        Parameters
        ----------
        logger : loguru.Logger
            If not supplied, it will instantiate a new logger.
        """
        self.logger = logger or get_logger()

    def on_get(self, req, resp):
        """Handle GET requests.

        After receiving a GET request a verification method is called to check
        whether it should send back success or failed.

        Parameters
        ----------
        req : falcon.Request
        resp : falcon.Response
        """
        if self._ok():
            resp.text = "OK"
            resp.status = falcon.HTTP_200  # OK.
        else:
            resp.text = "NOT OK"
            resp.status = falcon.HTTP_503  # Service unavailable.

    def _ok(self):
        """This method must be implemented by derived classes."""
        raise NotImplementedError()


class LivenessProbeListener(ProbeListener):
    """Listener for the endpoint /health."""

    def __init__(self):
        """Constructor of LivenessProbeListener"""
        self._is_running = True

    def close(self):
        """Close the ProbeListener.

        Set a flag to notify kubernetes that the service is no longer available.
        """
        self._is_running = False

    def _ok(self):
        """Implements endpoint-specific logic of /health.

        Returns
        -------
        bool : True if the application is running correctly. False otherwise.
        """

        return self._is_running


class ReadinessProbeListener(ProbeListener):
    """Listener for the endpoint /ready."""

    def _ok(self):
        """Implements endpoint-specific logic of /ready.

        Returns
        -------
        bool : True if the service is ready to handle requests adequately.
        False otherwise.
        """

        try:
            _ping_database()
        except DatabaseNotReadyError as err:
            self.logger.warn(str(err))

            return False

        return True


def _ping_database():
    with session_scope() as session:
        try:
            session.execute("SELECT 1")
        except sqlalchemy.exc.OperationalError:
            raise DatabaseNotReadyError("Operational error on database during ping.")
        except Exception as err:
            raise DatabaseNotReadyError(f"Unknown error during ping: {err}")
