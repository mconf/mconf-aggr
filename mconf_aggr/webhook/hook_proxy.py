import threading
import requests
import logging
import logaugment
import time

class WebhookProxyThread(threading.Thread):
    """ This class represents a thread to send hooks to another service by HTTP's requests.
    """
    def __init__(self, event, url, logger=None, **kwargs):
        """ Constructor of `WebhookProxyThread`.
        
        Parameters
        ----------
        event : str
            event to be sent.
        url : str
            url of the server which will receive the event.
        logger : logging.Logger
            If not supplied, it will instantiate a new logger from __name__.
        """
        threading.Thread.__init__(self, **kwargs)
        self._event = event
        self._url = url
        self.logger = logger or logging.getLogger(__name__)
        logaugment.add(self.logger, code="", site="", keywords="null")

    def _send_hook(self, event, url):
        """ Send hooks to another service by a HTTP POST request.
        
        Parameters
        ----------
        event : str
            event to be sent.
        url : str
            url of the server which will receive the event.
        """
        seconds = 5
        resp = ''
        while resp == '':
            try:
                logging_extra = {
                    "code": "HTTP Request POST",
                    "site": url,
                    "keywords": ["http", f"event={event}", "request", "POST"]
                }
                self.logger.debug("POSTing event.", extra=logging_extra)

                resp = requests.post(url=url, data=event)

                if not resp.ok:
                    logging_extra = {
                        "code": "HTTP Request error",
                        "site": url,
                        "keywords": ["http", f"server={url}", "error", "event", "request", "POST", f"status={resp.status_code}"]
                    }
                    self.logger.error(resp.reason or f"Error {resp.status_code}.", extra=logging_extra)
                break
            except requests.exceptions.ConnectionError:
                logging_extra = {
                    "code": "HTTP Connection refused.",
                    "site": url,
                    "keywords": ["http", f"server={url}", "error", "exception", "event", "request", "POST"]
                }
                self.logger.warn(f"Connection refused by the server. Sleeping for {seconds}", extra=logging_extra)

                time.sleep(seconds)

                continue
            except Exception as err:
                logging_extra = {
                    "code": "HTTP Request error",
                    "site": url,
                    "keywords": ["http", f"server={url}", "error", "exception", "event", "request", "POST"]
                }
                self.logger.error(f"Unknown exception: {err}", extra=logging_extra)
                raise Exception() from err
    
    def run(self):
        """ Runs the thread for '_send_hook' method.
        """

        self._send_hook(event=self._event, url=self._url)

    def send_hook(self):
        """ Starts thread and send hooks to another service by a HTTP POST request.
        """
        self.start()