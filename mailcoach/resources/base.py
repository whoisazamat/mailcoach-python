from collections.abc import Generator

from mailcoach.helpers.requestor import Requestor


class BaseResource:
    """Base class for all API resources."""

    endpoint_template: str = None
    required_params: dict[str, list[str]] = {}

    def __init__(self, requestor: Requestor):
        if not self.endpoint_template:
            error_message = "Subclasses must define endpoint_template"
            raise NotImplementedError(error_message)
        self.requestor = requestor

    def validate_required_params(self, method_name: str, kwargs: dict) -> None:
        """Ensure that all required parameters are provided for a specific method."""
        required_params = self.required_params.get(method_name, [])
        missing_params = [param for param in required_params if param not in kwargs]
        if missing_params:
            error_message = f"Missing required parameters for {method_name}: {', '.join(missing_params)}"
            raise ValueError(error_message)

    def get_all(self, *args: list, **kwargs: dict) -> Generator[dict, None, None]:
        """Retrieve all items from the resource with pagination support.

        *args is added to catch positional arguments and provide a clear error message if needed.
        """
        self.validate_required_params("get_all", kwargs)
        endpoint = self.endpoint_template.format(**kwargs)

        while endpoint:
            response = self.requestor.send_request("GET", endpoint)
            yield from response.get("data", [])
            endpoint = response.get("links", {}).get("next")

    def get(self, uuid: str, **kwargs: dict) -> dict:
        """Retrieve a specific item by UUID."""
        kwargs["uuid"] = uuid
        self.validate_required_params("get", kwargs)

        endpoint = f"{self.endpoint_template.format(**kwargs)}/{uuid}"
        response = self.requestor.send_request("GET", endpoint)
        return response.get("data", {})

    def add(self, data: dict, **kwargs: dict) -> dict:
        """Add a new item to the resource."""
        kwargs["data"] = data
        self.validate_required_params("add", kwargs)

        endpoint = self.endpoint_template.format(**kwargs)
        response = self.requestor.send_request("POST", endpoint, data=data)
        return response.get("data", {})

    def update(self, uuid: str, data: dict, **kwargs: dict) -> dict:
        """Update an existing item by UUID."""
        kwargs["uuid"] = uuid
        kwargs["data"] = data
        self.validate_required_params("update", kwargs)

        endpoint = f"{self.endpoint_template.format(**kwargs)}/{uuid}"
        response = self.requestor.send_request("PUT", endpoint, data=data)
        return response.get("data", {})

    def remove(self, uuid: str, **kwargs: dict[str, str]) -> dict:
        """Delete an item by UUID."""
        kwargs["uuid"] = uuid
        self.validate_required_params("remove", kwargs)

        endpoint = f"{self.endpoint_template.format(**kwargs)}/{uuid}"
        return self.requestor.send_request("DELETE", endpoint)
