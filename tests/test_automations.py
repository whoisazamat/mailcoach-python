from mailcoach.resources.automations import AutomationResource
from tests.conftest import UUID


def test_trigger_automation(mock_requestor):
    instance = AutomationResource(mock_requestor)

    instance.trigger(UUID, ["first-uuid", "second-uuid"])

    mock_requestor.send_request.assert_called_once_with(
        "POST", f"automations/{UUID}/trigger", data={"subscribers": ["first-uuid", "second-uuid"]},
    )
