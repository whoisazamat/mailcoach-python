from mailcoach.resources.base import BaseResource
from mailcoach.transport import Requestor


class AutomationMailResource(BaseResource):
    """Represent the Automation Mail resource."""

    endpoint_template = "automation-mails"


class AutomationResource:
    """Represent the Automation resource.

    Does not derive from ReadOnlyResource: triggering is the only automation operation the API
    exposes, so there is no collection or item endpoint for a base class to build on.
    """

    def __init__(self, requestor: Requestor) -> None:
        self.requestor = requestor

    def trigger(self, uuid: str, subscribers: list[str]) -> None:
        """Run the automation for the given subscriber UUIDs."""
        data = {"subscribers": subscribers}
        self.requestor.send_request("POST", f"automations/{uuid}/trigger", data=data)
