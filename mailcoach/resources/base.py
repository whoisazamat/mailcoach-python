from collections.abc import Iterator
from typing import Any, ClassVar

from mailcoach.helpers.requestor import Requestor


class BaseResource:
    """Base class for all API resources."""

    endpoint_template: ClassVar[str] = ""

    def __init__(self, requestor: Requestor) -> None:
        if not self.endpoint_template:
            error_message = f"{type(self).__name__} must define endpoint_template"
            raise NotImplementedError(error_message)
        self.requestor = requestor

    def _endpoint(self, **kwargs: str) -> str:
        """Fill the endpoint template, reporting a missing placeholder as a call-site error."""
        try:
            return self.endpoint_template.format(**kwargs)
        except KeyError as error:
            error_message = f"{type(self).__name__} requires keyword argument {error}"
            raise TypeError(error_message) from error

    def _paginate(self, endpoint: str) -> Iterator[dict[str, Any]]:
        """Yield every item across the pages the API links together."""
        next_endpoint: str | None = endpoint

        while next_endpoint:
            response = self.requestor.send_request("GET", next_endpoint)
            yield from response.get("data", [])
            next_endpoint = (response.get("links") or {}).get("next")

    def get_all(self, **kwargs: str) -> Iterator[dict[str, Any]]:
        """Retrieve all items from the resource with pagination support."""
        return self._paginate(self._endpoint(**kwargs))

    @staticmethod
    def _unwrap(response: dict[str, Any]) -> dict[str, Any]:
        """Take the item out of the envelope the API wraps single resources in."""
        data: dict[str, Any] = response.get("data", {})
        return data

    def get(self, uuid: str, **kwargs: str) -> dict[str, Any]:
        """Retrieve a specific item by UUID."""
        response = self.requestor.send_request("GET", f"{self._endpoint(**kwargs)}/{uuid}")
        return self._unwrap(response)

    def add(self, data: dict[str, Any], **kwargs: str) -> dict[str, Any]:
        """Add a new item to the resource."""
        response = self.requestor.send_request("POST", self._endpoint(**kwargs), data=data)
        return self._unwrap(response)

    def update(self, uuid: str, data: dict[str, Any], **kwargs: str) -> dict[str, Any]:
        """Update an existing item by UUID."""
        response = self.requestor.send_request("PUT", f"{self._endpoint(**kwargs)}/{uuid}", data=data)
        return self._unwrap(response)

    def delete(self, uuid: str, **kwargs: str) -> None:
        """Delete an item by UUID."""
        self.requestor.send_request("DELETE", f"{self._endpoint(**kwargs)}/{uuid}")
