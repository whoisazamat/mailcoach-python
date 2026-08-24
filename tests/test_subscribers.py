import pytest

from mailcoach.resources.subscribers import SubscriberResource
from tests.conftest import EMAIL_LIST_UUID, URL_ROOT, UUID


COLLECTION = f"email-lists/{EMAIL_LIST_UUID}/subscribers"
ITEM = f"subscribers/{UUID}"


@pytest.fixture
def subscribers(mock_requestor):
    return SubscriberResource(mock_requestor)


def test_get_all_lists_within_the_email_list(subscribers, mock_requestor, sample_response):
    mock_requestor.send_request.return_value = {"data": [sample_response]}

    results = list(subscribers.get_all(email_list_uuid=EMAIL_LIST_UUID))

    mock_requestor.send_request.assert_called_once_with("GET", COLLECTION)
    assert results == [sample_response]


def test_get_all_follows_pagination_links(subscribers, mock_requestor, sample_response):
    next_page = f"{URL_ROOT}/api/{COLLECTION}?page=2"
    mock_requestor.send_request.side_effect = [
        {"data": [sample_response], "links": {"next": next_page}},
        {"data": [sample_response], "links": {"next": None}},
    ]

    results = list(subscribers.get_all(email_list_uuid=EMAIL_LIST_UUID))

    assert [call.args for call in mock_requestor.send_request.call_args_list] == [
        ("GET", COLLECTION),
        ("GET", next_page),
    ]
    assert results == [sample_response, sample_response]


def test_add_posts_into_the_email_list(subscribers, mock_requestor, sample_data, sample_response):
    mock_requestor.send_request.return_value = {"data": sample_response}

    result = subscribers.add(sample_data, email_list_uuid=EMAIL_LIST_UUID)

    mock_requestor.send_request.assert_called_once_with("POST", COLLECTION, data=sample_data)
    assert result == sample_response


def test_get_addresses_the_subscriber_globally(subscribers, mock_requestor, sample_response):
    mock_requestor.send_request.return_value = {"data": sample_response}

    result = subscribers.get(UUID)

    mock_requestor.send_request.assert_called_once_with("GET", ITEM)
    assert result == sample_response


def test_update_uses_patch(subscribers, mock_requestor, sample_data, sample_response):
    mock_requestor.send_request.return_value = {"data": sample_response}

    result = subscribers.update(UUID, sample_data)

    mock_requestor.send_request.assert_called_once_with("PATCH", ITEM, data=sample_data)
    assert result == sample_response


def test_delete_addresses_the_subscriber_globally(subscribers, mock_requestor):
    mock_requestor.send_request.return_value = {}

    assert subscribers.delete(UUID) is None

    mock_requestor.send_request.assert_called_once_with("DELETE", ITEM)


@pytest.mark.parametrize(
    ("method", "action"),
    [
        ("confirm", "confirm"),
        ("unsubscribe", "unsubscribe"),
        ("resubscribe", "resubscribe"),
        ("resend_confirmation", "resend-confirmation"),
    ],
)
def test_actions_post_to_their_own_endpoint(subscribers, mock_requestor, method, action):
    assert getattr(subscribers, method)(UUID) is None

    mock_requestor.send_request.assert_called_once_with("POST", f"{ITEM}/{action}")


@pytest.mark.parametrize("method", ["get", "delete"])
def test_item_methods_reject_the_email_list_uuid(subscribers, mock_requestor, method):
    with pytest.raises(TypeError, match="unexpected keyword arguments: email_list_uuid"):
        getattr(subscribers, method)(UUID, email_list_uuid=EMAIL_LIST_UUID)

    mock_requestor.send_request.assert_not_called()


def test_get_all_still_requires_the_email_list_uuid(subscribers, mock_requestor):
    with pytest.raises(TypeError, match="requires keyword arguments: email_list_uuid"):
        subscribers.get_all()

    mock_requestor.send_request.assert_not_called()
