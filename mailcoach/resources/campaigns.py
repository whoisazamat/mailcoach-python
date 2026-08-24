from collections.abc import Iterator
from typing import Any

from mailcoach.resources.base import BaseResource


class CampaignResource(BaseResource):
    """Represent the Campaign resource."""

    endpoint_template = "campaigns"

    def schedule(self, uuid: str, schedule_at: str, data: dict[str, Any]) -> dict[str, Any]:
        """Schedule a campaign for delivery at the given time."""
        payload = {**data, "schedule_at": schedule_at}
        response = self.requestor.send_request("PUT", f"{self.endpoint_template}/{uuid}", data=payload)
        return self._unwrap(response)

    def send_test(self, uuid: str, email_list: list[str]) -> None:
        """Send a test copy of the campaign to the given addresses."""
        data = {"email": ",".join(email_list)}
        self.requestor.send_request("POST", f"{self.endpoint_template}/{uuid}/send-test", data=data)

    def send(self, uuid: str) -> None:
        """Send the campaign to its email list."""
        self.requestor.send_request("POST", f"{self.endpoint_template}/{uuid}/send")

    def opens(self, uuid: str) -> Iterator[dict[str, Any]]:
        """Iterate over the opens recorded for the campaign."""
        return self._paginate(f"{self.endpoint_template}/{uuid}/opens")

    def clicks(self, uuid: str) -> Iterator[dict[str, Any]]:
        """Iterate over the clicks recorded for the campaign."""
        return self._paginate(f"{self.endpoint_template}/{uuid}/clicks")

    def unsubscribes(self, uuid: str) -> Iterator[dict[str, Any]]:
        """Iterate over the unsubscribes recorded for the campaign."""
        return self._paginate(f"{self.endpoint_template}/{uuid}/unsubscribes")

    def bounces(self, uuid: str) -> Iterator[dict[str, Any]]:
        """Iterate over the bounces recorded for the campaign."""
        return self._paginate(f"{self.endpoint_template}/{uuid}/bounces")
