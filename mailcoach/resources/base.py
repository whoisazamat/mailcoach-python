from collections.abc import Iterator
from string import Formatter
from typing import Any, ClassVar
from urllib.parse import urlencode

from mailcoach.helpers.requestor import Requestor


class BaseResource:
    """Base class for all API resources."""

    endpoint_template: ClassVar[str] = ""

    def __init__(self, requestor: Requestor) -> None:
        if not self.endpoint_template:
            error_message = f"{type(self).__name__} must define endpoint_template"
            raise NotImplementedError(error_message)
        self.requestor = requestor

    @classmethod
    def _format(cls, template: str, **kwargs: str) -> str:
        """Fill a template, reporting both missing and unknown placeholders as call-site errors."""
        expected = {name for _, name, _, _ in Formatter().parse(template) if name}

        unknown = sorted(set(kwargs) - expected)
        if unknown:
            error_message = f"{cls.__name__} got unexpected keyword arguments: {', '.join(unknown)}"
            raise TypeError(error_message)

        missing = sorted(expected - set(kwargs))
        if missing:
            error_message = f"{cls.__name__} requires keyword arguments: {', '.join(missing)}"
            raise TypeError(error_message)

        return template.format(**kwargs)

    def _endpoint(self, **kwargs: str) -> str:
        """Path to the resource collection."""
        return self._format(self.endpoint_template, **kwargs)

    def _item_endpoint(self, uuid: str, **kwargs: str) -> str:
        """Path to a single item; resources whose items live elsewhere override this."""
        return f"{self._endpoint(**kwargs)}/{uuid}"

    @staticmethod
    def _filter_string(filters: dict[str, str] | None) -> str:
        """Render filters the way the API expects them: ?filter[name]=value."""
        if not filters:
            return ""

        return "?" + urlencode({f"filter[{name}]": value for name, value in filters.items()})

    def _paginate(self, endpoint: str) -> Iterator[dict[str, Any]]:
        """Yield every item across the pages the API links together."""
        next_endpoint: str | None = endpoint

        while next_endpoint:
            response = self.requestor.send_request("GET", next_endpoint)
            yield from response.get("data", [])
            next_endpoint = (response.get("links") or {}).get("next")

    @staticmethod
    def _unwrap(response: dict[str, Any]) -> dict[str, Any]:
        """Take the item out of the envelope the API wraps single resources in."""
        data: dict[str, Any] = response.get("data", {})
        return data

    def get_all(self, *, filters: dict[str, str] | None = None, **kwargs: str) -> Iterator[dict[str, Any]]:
        """Retrieve all items from the resource with pagination support, optionally narrowed by filters."""
        return self._paginate(self._endpoint(**kwargs) + self._filter_string(filters))

    def get(self, uuid: str, **kwargs: str) -> dict[str, Any]:
        """Retrieve a specific item by UUID."""
        response = self.requestor.send_request("GET", self._item_endpoint(uuid, **kwargs))
        return self._unwrap(response)

    def add(self, data: dict[str, Any], **kwargs: str) -> dict[str, Any]:
        """Add a new item to the resource."""
        response = self.requestor.send_request("POST", self._endpoint(**kwargs), data=data)
        return self._unwrap(response)

    def update(self, uuid: str, data: dict[str, Any], **kwargs: str) -> dict[str, Any]:
        """Update an existing item by UUID."""
        response = self.requestor.send_request("PUT", self._item_endpoint(uuid, **kwargs), data=data)
        return self._unwrap(response)

    def delete(self, uuid: str, **kwargs: str) -> None:
        """Delete an item by UUID."""
        self.requestor.send_request("DELETE", self._item_endpoint(uuid, **kwargs))
