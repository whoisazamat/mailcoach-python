import pytest

from mailcoach.resources.campaigns import CampaignResource
from tests.conftest import URL_ROOT, UUID


@pytest.fixture
def campaigns(mock_requestor):
    return CampaignResource(mock_requestor)


def test_schedule_sends_schedule_at(campaigns, mock_requestor, sample_data, sample_response):
    mock_requestor.send_request.return_value = {"data": sample_response}

    result = campaigns.schedule(UUID, "2025-01-01 18:00:00", sample_data)

    mock_requestor.send_request.assert_called_once_with(
        "PUT", f"campaigns/{UUID}", data={**sample_data, "schedule_at": "2025-01-01 18:00:00"},
    )
    assert result == sample_response


def test_schedule_does_not_mutate_caller_data(campaigns, mock_requestor, sample_data):
    mock_requestor.send_request.return_value = {}
    original = dict(sample_data)

    campaigns.schedule(UUID, "2025-01-01 18:00:00", sample_data)

    assert sample_data == original


def test_send_test_joins_addresses(campaigns, mock_requestor):
    campaigns.send_test(UUID, ["first@mailcoach.test", "second@mailcoach.test"])

    mock_requestor.send_request.assert_called_once_with(
        "POST", f"campaigns/{UUID}/send-test", data={"email": "first@mailcoach.test,second@mailcoach.test"},
    )


def test_send(campaigns, mock_requestor):
    campaigns.send(UUID)

    mock_requestor.send_request.assert_called_once_with("POST", f"campaigns/{UUID}/send")


@pytest.mark.parametrize("method", ["opens", "clicks", "unsubscribes", "bounces"])
def test_statistics_hit_their_own_endpoint(campaigns, mock_requestor, method, sample_response):
    mock_requestor.send_request.return_value = {"data": [sample_response]}

    results = list(getattr(campaigns, method)(UUID))

    mock_requestor.send_request.assert_called_once_with("GET", f"campaigns/{UUID}/{method}")
    assert results == [sample_response]


@pytest.mark.parametrize("method", ["opens", "clicks", "unsubscribes", "bounces"])
def test_statistics_follow_pagination_links(campaigns, mock_requestor, method, sample_response):
    next_page = f"{URL_ROOT}/api/campaigns/{UUID}/{method}?page=2"
    mock_requestor.send_request.side_effect = [
        {"data": [sample_response], "links": {"next": next_page}},
        {"data": [sample_response], "links": {"next": None}},
    ]

    results = list(getattr(campaigns, method)(UUID))

    assert [call.args for call in mock_requestor.send_request.call_args_list] == [
        ("GET", f"campaigns/{UUID}/{method}"),
        ("GET", next_page),
    ]
    assert results == [sample_response, sample_response]
