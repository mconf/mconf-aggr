class WebhookError(Exception):
    """Raised if any error occurrs in the webhook app.

    It is a generic error intended to be extended by other more specific errors.
    """
    pass


class RequestProcessingError(WebhookError):
    """Raised if an error occurrs while processing a request received.
    """
    pass


class InvalidWebhookMessageError(WebhookError):
    """Raised if there is any problem in the body of the request.
    """
    pass


class InvalidWebhookEventError(WebhookError):
    """Raised if the type of the event received is not valid or known.
    """
    pass


class WebhookDatabaseError(WebhookError):
    """Raised if any error occurrs while interacting with the database.
    """
    pass

class DatabaseNotReadyError(WebhookError):
    """Raised if the database does not seem ready for connections.
    """
