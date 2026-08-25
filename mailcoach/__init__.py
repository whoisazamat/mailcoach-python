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


__version__ = "0.1.0"

__all__ = [
    "APIError",
    "AuthenticationError",
    "MailCoachClient",
    "MailcoachError",
    "NotFoundError",
    "RateLimitError",
    "RequestError",
    "ValidationError",
    "__version__",
]
