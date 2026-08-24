import pytest

from mailcoach.resources.campaigns import CampaignResource
from mailcoach.resources.email_lists import EmailListResource
from mailcoach.resources.segments import SegmentResource
from mailcoach.resources.tags import TagResource
from tests.conftest import EMAIL_LIST_UUID, URL_ROOT, UUID


RESOURCES = [
    (EmailListResource, {}, "email-lists"),
    (TagResource, {"email_list_uuid": EMAIL_LIST_UUID}, f"email-lists/{EMAIL_LIST_UUID}/tags"),
    (SegmentResource, {"email_list_uuid": EMAIL_LIST_UUID}, f"email-lists/{EMAIL_LIST_UUID}/segments"),
    (CampaignResource, {}, "campaigns"),
]


@pytest.mark.parametrize(("resource", "kwargs", "endpoint"), RESOURCES)
def test_get_all(resource, kwargs, endpoint, mock_requestor, sample_response):
    instance = resource(mock_requestor)
    mock_requestor.send_request.return_value = {"data": [sample_response]}

    results = list(instance.get_all(**kwargs))

    mock_requestor.send_request.assert_called_once_with("GET", endpoint)
    assert results == [sample_response]


@pytest.mark.parametrize(("resource", "kwargs", "endpoint"), RESOURCES)
def test_get_all_follows_pagination_links(resource, kwargs, endpoint, mock_requestor, sample_response):
    # links.next comes back absolute; get_all must keep requesting until the API stops handing one out.
    next_page = f"{URL_ROOT}/api/{endpoint}?page=2"
    mock_requestor.send_request.side_effect = [
        {"data": [sample_response], "links": {"next": next_page}},
        {"data": [sample_response], "links": {"next": None}},
    ]

    results = list(resource(mock_requestor).get_all(**kwargs))

    assert [call.args for call in mock_requestor.send_request.call_args_list] == [
        ("GET", endpoint),
        ("GET", next_page),
    ]
    assert results == [sample_response, sample_response]


@pytest.mark.parametrize(("resource", "kwargs", "endpoint"), RESOURCES)
def test_get(resource, kwargs, endpoint, mock_requestor, sample_response):
    instance = resource(mock_requestor)
    mock_requestor.send_request.return_value = {"data": sample_response}

    result = instance.get(UUID, **kwargs)

    mock_requestor.send_request.assert_called_once_with("GET", f"{endpoint}/{UUID}")
    assert result == sample_response


@pytest.mark.parametrize(("resource", "kwargs", "endpoint"), RESOURCES)
def test_add(resource, kwargs, endpoint, mock_requestor, sample_data, sample_response):
    instance = resource(mock_requestor)
    mock_requestor.send_request.return_value = {"data": sample_response}

    result = instance.add(sample_data, **kwargs)

    mock_requestor.send_request.assert_called_once_with("POST", endpoint, data=sample_data)
    assert result == sample_response


@pytest.mark.parametrize(("resource", "kwargs", "endpoint"), RESOURCES)
def test_update(resource, kwargs, endpoint, mock_requestor, sample_data, sample_response):
    instance = resource(mock_requestor)
    mock_requestor.send_request.return_value = {"data": sample_response}

    result = instance.update(UUID, sample_data, **kwargs)

    mock_requestor.send_request.assert_called_once_with("PUT", f"{endpoint}/{UUID}", data=sample_data)
    assert result == sample_response


@pytest.mark.parametrize(("resource", "kwargs", "endpoint"), RESOURCES)
def test_delete(resource, kwargs, endpoint, mock_requestor):
    instance = resource(mock_requestor)
    mock_requestor.send_request.return_value = {}

    assert instance.delete(UUID, **kwargs) is None

    mock_requestor.send_request.assert_called_once_with("DELETE", f"{endpoint}/{UUID}")


@pytest.mark.parametrize(("resource", "kwargs", "_endpoint"), RESOURCES)
def test_unknown_keyword_argument_is_rejected(resource, kwargs, _endpoint, mock_requestor):
    instance = resource(mock_requestor)

    with pytest.raises(TypeError, match="unexpected keyword arguments: nonsense"):
        instance.get_all(nonsense="x", **kwargs)

    mock_requestor.send_request.assert_not_called()


@pytest.mark.parametrize(("resource", "kwargs", "_endpoint"), RESOURCES)
def test_missing_data_key_yields_empty_result(resource, kwargs, _endpoint, mock_requestor):
    instance = resource(mock_requestor)
    mock_requestor.send_request.return_value = {}

    assert instance.get(UUID, **kwargs) == {}
    assert list(instance.get_all(**kwargs)) == []


def test_endpoint_template_is_required(mock_requestor):
    class NamelessResource(EmailListResource):
        endpoint_template = ""

    with pytest.raises(NotImplementedError, match="endpoint_template"):
        NamelessResource(mock_requestor)


@pytest.mark.parametrize(("method", "args"), [
    ("get_all", ()),
    ("get", (UUID,)),
    ("add", ({},)),
    ("update", (UUID, {})),
    ("delete", (UUID,)),
])
def test_missing_template_argument_raises_at_call_time(method, args, mock_requestor):
    instance = TagResource(mock_requestor)

    with pytest.raises(TypeError, match="email_list_uuid"):
        getattr(instance, method)(*args)

    mock_requestor.send_request.assert_not_called()
