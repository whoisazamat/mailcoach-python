from typing import Any


class MailcoachError(Exception):
    """Base class for every error this library raises."""


class RequestError(MailcoachError):
    """The request never produced a usable response: transport failure, or a body that would not decode."""


class APIError(MailcoachError):
    """The API answered with a non-2xx status."""

    def __init__(
        self,
        message: str,
        status_code: int,
        body: dict[str, Any] | None = None,
        retry_after: int | None = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.body = body or {}
        self.retry_after = retry_after


class AuthenticationError(APIError):
    """The token is missing, invalid, or not allowed to touch this resource (401, 403)."""


class NotFoundError(APIError):
    """No resource matches the given identifier (404)."""


class ValidationError(APIError):
    """The payload was rejected field by field (422)."""

    @property
    def errors(self) -> dict[str, list[str]]:
        """Field name to the list of messages the API returned for it."""
        return self.body.get("errors", {})


class RateLimitError(APIError):
    """Too many requests in the current window (429); retry_after holds the seconds to wait, when sent."""
