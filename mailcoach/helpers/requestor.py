import requests

from mailcoach.exceptions import RequestError


class Requestor:
    def __init__(self, url_root: str, token: str, request_headers: dict):
        self.url_root = url_root
        self.token = token
        self.request_headers = request_headers

    def send_request(self, method: str, url: str, data: dict | None = None) -> dict:
        """Send a request to the MailCoach API."""
        try:
            response = requests.request(
                method,
                url,
                headers=self.request_headers,
                json=data,
            )
        except requests.exceptions.RequestException as error:
            raise RequestError(error)

        return response.json()
