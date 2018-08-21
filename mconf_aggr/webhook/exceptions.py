class WebhookError(Exception):
    pass


class RequestProcessingError(WebhookError):
    pass


class InvalidWebhookMessage(WebhookError):
    pass


class InvalidWebhookEvent(WebhookError):
    pass
