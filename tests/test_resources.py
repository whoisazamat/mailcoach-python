from unittest.mock import MagicMock

import pytest

from mailcoach.resources.email_lists import EmailListResource
from mailcoach.resources.tags import TagResource
from mailcoach.resources.segments import SegmentResource


@pytest.mark.parametrize("resource, required_kwargs, endpoint", [
    (EmailListResource, {}, "email-lists"),
    (TagResource, {"email_list_uuid": "test-email-list-uuid"}, "email-lists/test-email-list-uuid/tags"),
    (SegmentResource, {"email_list_uuid": "test-email-list-uuid"}, "email-lists/test-email-list-uuid/segments"),
])
def test_get_all(resource, required_kwargs, endpoint, mock_requestor, sample_response):
    instance = resource(mock_requestor)
    mock_requestor.send_request.return_value = {"data": [sample_response]}

    results = list(instance.get_all(**required_kwargs))

    mock_requestor.send_request.assert_called_once_with("GET", endpoint)
    assert results == [sample_response]


@pytest.mark.parametrize("resource, required_kwargs, uuid, endpoint", [
    (EmailListResource, {}, "test-uuid", "email-lists/test-uuid"),
    (TagResource, {"email_list_uuid": "test-email-list-uuid"}, "test-uuid", "email-lists/test-email-list-uuid/tags/test-uuid"),
    (SegmentResource, {"email_list_uuid": "test-email-list-uuid"}, "test-uuid", "email-lists/test-email-list-uuid/segments/test-uuid"),
])
def test_get(resource, required_kwargs, uuid, endpoint, mock_requestor, sample_response):
    instance = resource(mock_requestor)
    mock_requestor.send_request.return_value = {"data": sample_response}

    result = instance.get(uuid, **required_kwargs)

    mock_requestor.send_request.assert_called_once_with("GET", endpoint)
    assert result == sample_response


@pytest.mark.parametrize("resource, required_kwargs, uuid, endpoint", [
    (EmailListResource, {}, "test-uuid", "email-lists/test-uuid"),
    (TagResource, {"email_list_uuid": "test-email-list-uuid"}, "test-uuid", "email-lists/test-email-list-uuid/tags/test-uuid"),
    (SegmentResource, {"email_list_uuid": "test-email-list-uuid"}, "test-uuid", "email-lists/test-email-list-uuid/segments/test-uuid"),
])
def test_update(resource, required_kwargs, uuid, endpoint, mock_requestor, sample_data, sample_response):
    instance = resource(mock_requestor)
    mock_requestor.send_request.return_value = {"data": sample_response}
    required_kwargs["data"] = sample_data
    result = instance.update(uuid, **required_kwargs)

    mock_requestor.send_request.assert_called_once_with("PUT", endpoint, data=sample_data)
    assert result == sample_response


@pytest.mark.parametrize("resource, required_kwargs, uuid, endpoint", [
    (EmailListResource, {}, "test-uuid", "email-lists/test-uuid"),
    (TagResource, {"email_list_uuid": "test-email-list-uuid"}, "test-uuid", "email-lists/test-email-list-uuid/tags/test-uuid"),
    (SegmentResource, {"email_list_uuid": "test-email-list-uuid"}, "test-uuid", "email-lists/test-email-list-uuid/segments/test-uuid"),
])
def test_remove(resource, required_kwargs, uuid, endpoint, mock_requestor):
    instance = resource(mock_requestor)
    mock_requestor.send_request.return_value = {"status": "OK"}

    result = instance.remove(uuid, **required_kwargs)

    mock_requestor.send_request.assert_called_once_with("DELETE", endpoint)
    assert result == {"status": "OK"}


@pytest.mark.parametrize("resource, required_kwargs, expected_error", [
    (TagResource, {}, "Missing required parameters for get_all: email_list_uuid"),
    (SegmentResource, {}, "Missing required parameters for get_all: email_list_uuid"),
])
def test_get_all_missing_param(resource, required_kwargs, expected_error):
    instance = resource(MagicMock())

    with pytest.raises(ValueError, match=expected_error):
        list(instance.get_all(**required_kwargs))
