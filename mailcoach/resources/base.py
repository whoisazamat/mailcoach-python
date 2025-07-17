from collections.abc import Generator

from mailcoach.helpers.requestor import Requestor


class BaseResource:
    """Base class for all API resources."""

    endpoint_template: str = None

    def __init__(self, requestor: Requestor):
        if not self.endpoint_template:
            error_message = "Subclasses must define endpoint_template"
            raise NotImplementedError(error_message)
        self.requestor = requestor

    def get_all(self, **kwargs: dict) -> Generator[dict, None, None]:
        """Retrieve all items from the resource with pagination support."""
        endpoint = self.endpoint_template.format(**kwargs)

        while endpoint:
            response = self.requestor.send_request("GET", endpoint)
            yield from response.get("data", [])
            endpoint = response.get("links", {}).get("next")

    def get(self, uuid: str, **kwargs: dict) -> dict:
        """Retrieve a specific item by UUID."""
        endpoint = f"{self.endpoint_template.format(**kwargs)}/{uuid}"
        response = self.requestor.send_request("GET", endpoint)
        return response.get("data", {})

    def add(self, data: dict, **kwargs: dict) -> dict:
        """Add a new item to the resource."""
        endpoint = self.endpoint_template.format(**kwargs)
        response = self.requestor.send_request("POST", endpoint, data=data)
        return response.get("data", {})

    def update(self, uuid: str, data: dict, **kwargs: dict) -> dict:
        """Update an existing item by UUID."""
        endpoint = f"{self.endpoint_template.format(**kwargs)}/{uuid}"
        response = self.requestor.send_request("PUT", endpoint, data=data)
        return response.get("data", {})

    def remove(self, uuid: str, **kwargs: dict[str, str]) -> dict:
        """Delete an item by UUID."""
        endpoint = f"{self.endpoint_template.format(**kwargs)}/{uuid}"
        return self.requestor.send_request("DELETE", endpoint)
