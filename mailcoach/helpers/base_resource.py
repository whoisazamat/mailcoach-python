from collections.abc import Generator

from mailcoach.helpers.requestor import Requestor


class BaseResource:
    def __init__(self, requestor: Requestor):
        self.requestor = requestor

    def iter_all(self, endpoint: str) -> Generator[dict, None, None]:
        while endpoint:
            response = self.requestor.send_request("GET", endpoint)
            yield from response.get("data", [])

            endpoint = response.get("links", {}).get("next")
