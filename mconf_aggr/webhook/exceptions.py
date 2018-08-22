class WebhookError(Exception):
    pass


class RequestProcessingError(WebhookError):
    pass


class InvalidWebhookMessageError(WebhookError):
    pass


class InvalidWebhookEventError(WebhookError):
    pass


class WebhookDatabaseError(WebhookError):
    pass
