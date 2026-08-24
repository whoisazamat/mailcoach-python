from typing import Any

from mailcoach.resources.base import ReadOnlyResource


class TransactionalMailResource(ReadOnlyResource):
    """Represent the Transactional Mail resource.

    Read-only plus send(): the API records transactional mails as they go out, so there is nothing
    to create, update or delete after the fact.
    """

    endpoint_template = "transactional-mails"

    def send(self, data: dict[str, Any]) -> dict[str, Any]:
        """Send a transactional mail."""
        response = self.requestor.send_request("POST", f"{self.endpoint_template}/send", data=data)
        return self._unwrap(response)


class TransactionalMailTemplateResource(ReadOnlyResource):
    """Represent the Transactional Mail Template resource."""

    endpoint_template = "transactional-mails/templates"
