from http import HTTPStatus

import requests

from mailcoach.exceptions import RequestError


class Requestor:
    def __init__(self, url_root: str, token: str, request_headers: dict):
        self.url_root = url_root.rstrip("/")
        self.token = token
        self.request_headers = request_headers

    def _build_url(self, relative_path: str) -> str:
        """Build the full API URL from the relative path."""
        return f"{self.url_root}/api/{relative_path.lstrip('/')}"

    def send_request(self, method: str, url: str, data: dict | None = None) -> dict:
        """Send a request to the MailCoach API."""
        full_url = self._build_url(url)

        try:
            response = requests.request(
                method,
                full_url,
                headers=self.request_headers,
                json=data,
            )
        except requests.exceptions.RequestException as error:
            raise RequestError(error)

        if response.status_code != HTTPStatus.OK:
            error_message = f"Unexpected response {response.status_code}: {response.text}"
            raise RequestError(error_message)

        if response.status_code == HTTPStatus.NO_CONTENT:
            return {"status": "OK"}

        return response.json()
