from mailcoach.client import MailCoachClient
from mailcoach.exceptions import (
    APIError,
    AuthenticationError,
    MailcoachError,
    NotFoundError,
    RateLimitError,
    RequestError,
    ValidationError,
)


__all__ = [
    "APIError",
    "AuthenticationError",
    "MailCoachClient",
    "MailcoachError",
    "NotFoundError",
    "RateLimitError",
    "RequestError",
    "ValidationError",
]
