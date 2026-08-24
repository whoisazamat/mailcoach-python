import pytest

from mailcoach.resources.transactional import TransactionalMailResource, TransactionalMailTemplateResource
from tests.conftest import UUID


@pytest.mark.parametrize(
    ("resource", "endpoint"),
    [
        (TransactionalMailResource, "transactional-mails"),
        (TransactionalMailTemplateResource, "transactional-mails/templates"),
    ],
)
def test_read_only_resources_list_and_get(resource, endpoint, mock_requestor, sample_response):
    instance = resource(mock_requestor)
    mock_requestor.send_request.return_value = {"data": sample_response}

    assert instance.get(UUID) == sample_response

    mock_requestor.send_request.assert_called_once_with("GET", f"{endpoint}/{UUID}")


@pytest.mark.parametrize(
    ("resource", "method"),
    [
        (TransactionalMailResource, "add"),
        (TransactionalMailResource, "update"),
        (TransactionalMailResource, "delete"),
        (TransactionalMailTemplateResource, "add"),
        (TransactionalMailTemplateResource, "update"),
        (TransactionalMailTemplateResource, "delete"),
    ],
)
def test_read_only_resources_expose_no_writes(resource, method, mock_requestor):
    assert not hasattr(resource(mock_requestor), method)


def test_send_transactional_mail(mock_requestor, sample_response):
    instance = TransactionalMailResource(mock_requestor)
    mock_requestor.send_request.return_value = {"data": sample_response}
    data = {"mail_name": "welcome", "to": "john@example.com"}

    result = instance.send(data)

    mock_requestor.send_request.assert_called_once_with("POST", "transactional-mails/send", data=data)
    assert result == sample_response
