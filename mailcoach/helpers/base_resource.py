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

    def add_item(self, endpoint: str, data: dict) -> dict:
        response = self.requestor.send_request(
            method="POST",
            url=endpoint,
            data=data,
        )
        return response.get("data", {})

    def update_item(self, endpoint: str, uuid: str, data: dict) -> dict:
        response = self.requestor.send_request(
            method="PUT",
            url=f"/{endpoint}/{uuid}",
            data=data,
        )
        return response.get("data", {})
