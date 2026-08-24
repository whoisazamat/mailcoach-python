from types import TracebackType
from typing import Any
from urllib.parse import urlsplit

import requests

from mailcoach.exceptions import RequestError


DEFAULT_TIMEOUT = 30.0


class Requestor:
    """Send HTTP requests to the Mailcoach API and unwrap their JSON bodies."""

    def __init__(self, url_root: str, token: str, timeout: float = DEFAULT_TIMEOUT):
        self.url_root = url_root.rstrip("/")
        self.timeout = timeout
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

    def send_request(self, method: str, url: str, data: dict | None = None) -> dict[str, Any]:
        """Send a request to the MailCoach API and return its decoded body, or {} when it has none."""
        full_url = self._build_url(url)

        try:
            response = self.session.request(method, full_url, json=data, timeout=self.timeout)
        except requests.exceptions.RequestException as error:
            error_message = f"{method} {full_url} failed: {error}"
            raise RequestError(error_message) from error

        if not response.ok:
            error_message = f"Unexpected response {response.status_code}: {response.text}"
            raise RequestError(error_message)

        if not response.content:
            return {}

        try:
            return response.json()
        except ValueError as error:
            error_message = f"Malformed JSON in response to {method} {full_url}: {response.text[:200]}"
            raise RequestError(error_message) from error

    def close(self) -> None:
        """Release the underlying connection pool."""
        self.session.close()

    def __enter__(self) -> "Requestor":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()
