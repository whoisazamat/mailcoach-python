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

    def get_specific_item(self, endpoint: str, uuid: str) -> dict:
        """Retrieve specific data by uuid."""
        response = self.requestor.send_request(
            method="GET",
            url=f"/{endpoint}/{uuid}",
        )
        return response.get("data", {})
