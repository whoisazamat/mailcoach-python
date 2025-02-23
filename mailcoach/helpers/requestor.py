import requests

from mailcoach.exceptions import RequestError


class Requestor:
    def __init__(self, url_root: str, token: str, request_headers: dict):
        self.url_root = url_root.rstrip("/")
        self.token = token
        self.request_headers = request_headers

    def _build_url(self, url: str) -> str:
        return f"{self.url_root}/api/{url.lstrip('/')}"

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

        return response.json()
