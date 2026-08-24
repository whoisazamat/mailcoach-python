from typing import Any

from mailcoach.resources.base import BaseResource


class SubscriberResource(BaseResource):
    """Represent the Subscriber resource.

    Inherits from BaseResource because listing and creation are ordinary nested-collection calls, so
    get_all() and add() work unchanged. Only two things diverge: a subscriber is addressed globally
    by its own UUID rather than under its email list, and the API updates it with PATCH instead of
    PUT — which is why _item_endpoint() and update() are the sole overrides.
    """

    endpoint_template = "email-lists/{email_list_uuid}/subscribers"

    def _item_endpoint(self, uuid: str, **kwargs: str) -> str:
        """Address the subscriber by its own UUID, not under the email list it was created in."""
        return self._format("subscribers/{uuid}", uuid=uuid, **kwargs)

    def update(self, uuid: str, data: dict[str, Any], **kwargs: str) -> dict[str, Any]:
        """Update an existing subscriber; this endpoint expects PATCH rather than PUT."""
        response = self.requestor.send_request("PATCH", self._item_endpoint(uuid, **kwargs), data=data)
        return self._unwrap(response)

    def confirm(self, uuid: str) -> None:
        """Complete the subscriber's double opt-in."""
        self.requestor.send_request("POST", f"subscribers/{uuid}/confirm")

    def unsubscribe(self, uuid: str) -> None:
        """Unsubscribe the subscriber from its email list."""
        self.requestor.send_request("POST", f"subscribers/{uuid}/unsubscribe")

    def resubscribe(self, uuid: str) -> None:
        """Undo an unsubscribe."""
        self.requestor.send_request("POST", f"subscribers/{uuid}/resubscribe")

    def resend_confirmation(self, uuid: str) -> None:
        """Send the double opt-in confirmation mail again."""
        self.requestor.send_request("POST", f"subscribers/{uuid}/resend-confirmation")
