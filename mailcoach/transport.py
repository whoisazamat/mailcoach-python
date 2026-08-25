import time
from http import HTTPStatus
from types import TracebackType
from typing import Any, Self
from urllib.parse import urlsplit

import requests

from mailcoach.exceptions import (
    APIError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    RequestError,
    ValidationError,
)


DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_ATTEMPTS = 3
DEFAULT_MAX_RETRY_WAIT = 60.0
RETRY_BACKOFF = 1.0

STATUS_ERRORS: dict[int, type[APIError]] = {
    HTTPStatus.UNAUTHORIZED: AuthenticationError,
    HTTPStatus.FORBIDDEN: AuthenticationError,
    HTTPStatus.NOT_FOUND: NotFoundError,
    HTTPStatus.UNPROCESSABLE_ENTITY: ValidationError,
    HTTPStatus.TOO_MANY_REQUESTS: RateLimitError,
}


class Requestor:
    """Send HTTP requests to the Mailcoach API and unwrap their JSON bodies."""

    def __init__(
        self,
        url_root: str,
        token: str,
        timeout: float = DEFAULT_TIMEOUT,
        max_attempts: int = DEFAULT_MAX_ATTEMPTS,
        max_retry_wait: float = DEFAULT_MAX_RETRY_WAIT,
    ) -> None:
        if max_attempts < 1:
            error_message = f"max_attempts must be at least 1, got {max_attempts}"
            raise ValueError(error_message)

        self.url_root = url_root.rstrip("/")
        self.timeout = timeout
        self.max_attempts = max_attempts
        self.max_retry_wait = max_retry_wait
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
        })

    def _build_url(self, relative_path: str) -> str:
        """Build the full API URL, passing through absolute URLs taken from pagination links."""
        if not relative_path.startswith(("http://", "https://")):
            return f"{self.url_root}/api/{relative_path.lstrip('/')}"

        if urlsplit(relative_path).netloc != urlsplit(self.url_root).netloc:
            error_message = f"Refusing to follow URL outside {self.url_root}: {relative_path}"
            raise RequestError(error_message)

        return relative_path

    @staticmethod
    def _raise_for_status(response: requests.Response) -> None:
        """Translate a non-2xx response into the exception type that matches its status."""
        if response.ok:
            return

        try:
            body = response.json()
        except ValueError:
            body = {}
        if not isinstance(body, dict):
            body = {}

        detail = body.get("message") or response.text[:200] or "no details"
        error_message = f"Unexpected response {response.status_code}: {detail}"

        retry_after = response.headers.get("Retry-After")
        error_class = STATUS_ERRORS.get(response.status_code, APIError)

        raise error_class(
            error_message,
            status_code=response.status_code,
            body=body,
            retry_after=int(retry_after) if retry_after and retry_after.isdigit() else None,
        )

    @staticmethod
    def _is_retryable(status_code: int) -> bool:
        """Say whether the status is one a later attempt could plausibly get past."""
        return status_code == HTTPStatus.TOO_MANY_REQUESTS or status_code >= HTTPStatus.INTERNAL_SERVER_ERROR

    def _retry_delay(self, attempt: int, retry_after: int | None) -> float:
        """Honour Retry-After when the API sends it, and back off exponentially when it does not."""
        if retry_after is not None:
            return float(retry_after)

        return RETRY_BACKOFF * float(2 ** (attempt - 1))

    def _should_retry(self, attempt: int, waited: float, delay: float) -> bool:
        """Allow another attempt only within both the attempt cap and the total wait budget."""
        return attempt < self.max_attempts and waited + delay <= self.max_retry_wait

    def _decode(self, response: requests.Response, method: str, full_url: str) -> dict[str, Any]:
        """Return the decoded body, or {} when the response has none."""
        if not response.content:
            return {}

        try:
            body: dict[str, Any] = response.json()
        except ValueError as error:
            error_message = f"Malformed JSON in response to {method} {full_url}: {response.text[:200]}"
            raise RequestError(error_message) from error

        return body

    def send_request(self, method: str, url: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
        """Send a request to the MailCoach API and return its decoded body, or {} when it has none.

        Rate limits and transient faults are retried here rather than by callers, so that pagination
        in get_all() survives a 429 mid-iteration without the caller seeing a partially consumed list.
        """
        full_url = self._build_url(url)
        attempt = 1
        waited = 0.0

        while True:
            try:
                response = self.session.request(method, full_url, json=data, timeout=self.timeout)
            except requests.exceptions.RequestException as error:
                delay = self._retry_delay(attempt, None)
                if not self._should_retry(attempt, waited, delay):
                    error_message = f"{method} {full_url} failed: {error}"
                    raise RequestError(error_message) from error
            else:
                try:
                    self._raise_for_status(response)
                except APIError as error:
                    delay = self._retry_delay(attempt, error.retry_after)
                    if not self._is_retryable(error.status_code) or not self._should_retry(attempt, waited, delay):
                        raise
                else:
                    return self._decode(response, method, full_url)

            time.sleep(delay)
            waited += delay
            attempt += 1

    def close(self) -> None:
        """Release the underlying connection pool."""
        self.session.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()
