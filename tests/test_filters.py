import pytest

from mailcoach.resources.base import BaseResource
from mailcoach.resources.email_lists import EmailListResource
from mailcoach.resources.subscribers import SubscriberResource
from tests.conftest import EMAIL_LIST_UUID, URL_ROOT


COLLECTION = f"email-lists/{EMAIL_LIST_UUID}/subscribers"


@pytest.mark.parametrize(
    ("filters", "expected"),
    [
        (None, ""),
        ({}, ""),
        ({"email": "john@example.com"}, "?filter%5Bemail%5D=john%40example.com"),
        ({"name": "a b"}, "?filter%5Bname%5D=a+b"),
        ({"email": "a@b.co", "name": "x"}, "?filter%5Bemail%5D=a%40b.co&filter%5Bname%5D=x"),
    ],
)
def test_filter_string(filters, expected):
    assert BaseResource._filter_string(filters) == expected


def test_get_all_appends_filters(mock_requestor, sample_response):
    instance = EmailListResource(mock_requestor)
    mock_requestor.send_request.return_value = {"data": [sample_response]}

    list(instance.get_all(filters={"name": "weekly"}))

    mock_requestor.send_request.assert_called_once_with("GET", "email-lists?filter%5Bname%5D=weekly")


def test_get_all_without_filters_is_unchanged(mock_requestor, sample_response):
    instance = EmailListResource(mock_requestor)
    mock_requestor.send_request.return_value = {"data": [sample_response]}

    list(instance.get_all())

    mock_requestor.send_request.assert_called_once_with("GET", "email-lists")


def test_filters_survive_pagination(mock_requestor, sample_response):
    first = f"{COLLECTION}?filter%5Bemail%5D=john%40example.com"
    next_page = f"{URL_ROOT}/api/{first}&page=2"
    mock_requestor.send_request.side_effect = [
        {"data": [sample_response], "links": {"next": next_page}},
        {"data": [sample_response], "links": {"next": None}},
    ]
    instance = SubscriberResource(mock_requestor)

    results = list(instance.get_all(filters={"email": "john@example.com"}, email_list_uuid=EMAIL_LIST_UUID))

    assert [call.args for call in mock_requestor.send_request.call_args_list] == [
        ("GET", first),
        ("GET", next_page),
    ]
    assert results == [sample_response, sample_response]


def test_find_by_email_returns_the_match(mock_requestor, sample_response):
    instance = SubscriberResource(mock_requestor)
    mock_requestor.send_request.return_value = {"data": [sample_response]}

    result = instance.find_by_email("john@example.com", email_list_uuid=EMAIL_LIST_UUID)

    mock_requestor.send_request.assert_called_once_with(
        "GET", f"{COLLECTION}?filter%5Bemail%5D=john%40example.com",
    )
    assert result == sample_response


def test_find_by_email_returns_none_when_absent(mock_requestor):
    instance = SubscriberResource(mock_requestor)
    mock_requestor.send_request.return_value = {"data": []}

    assert instance.find_by_email("nobody@example.com", email_list_uuid=EMAIL_LIST_UUID) is None


def test_find_by_email_still_requires_the_email_list_uuid(mock_requestor):
    instance = SubscriberResource(mock_requestor)

    with pytest.raises(TypeError, match="requires keyword arguments: email_list_uuid"):
        instance.find_by_email("john@example.com")

    mock_requestor.send_request.assert_not_called()
