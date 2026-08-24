import pytest

from mailcoach.exceptions import (
    APIError,
    AuthenticationError,
    MailcoachError,
    NotFoundError,
    RateLimitError,
    RequestError,
    ValidationError,
)

from tests.conftest import URL_ROOT


@pytest.mark.parametrize("status_code, error_class", [
    (401, AuthenticationError),
    (403, AuthenticationError),
    (404, NotFoundError),
    (422, ValidationError),
    (429, RateLimitError),
    (400, APIError),
    (500, APIError),
    (503, APIError),
])
def test_status_maps_to_error_class(requestor, requests_mock, status_code, error_class):
    requests_mock.get(f"{URL_ROOT}/api/campaigns", status_code=status_code, json={"message": "nope"})

    with pytest.raises(error_class) as error:
        requestor.send_request("GET", "campaigns")

    assert type(error.value) is error_class
    assert error.value.status_code == status_code


@pytest.mark.parametrize("error_class", [APIError, RequestError])
def test_every_error_is_a_mailcoach_error(error_class):
    assert issubclass(error_class, MailcoachError)


def test_api_error_carries_message_and_body(requestor, requests_mock):
    requests_mock.get(f"{URL_ROOT}/api/campaigns", status_code=404, json={"message": "No such campaign"})

    with pytest.raises(NotFoundError) as error:
        requestor.send_request("GET", "campaigns")

    assert "No such campaign" in str(error.value)
    assert error.value.body == {"message": "No such campaign"}


def test_validation_error_exposes_field_errors(requestor, requests_mock):
    body = {"message": "The given data was invalid.", "errors": {"name": ["The name field is required."]}}
    requests_mock.post(f"{URL_ROOT}/api/campaigns", status_code=422, json=body)

    with pytest.raises(ValidationError) as error:
        requestor.send_request("POST", "campaigns", data={})

    assert error.value.errors == {"name": ["The name field is required."]}


def test_rate_limit_error_exposes_retry_after(requestor, requests_mock):
    requests_mock.get(f"{URL_ROOT}/api/campaigns", status_code=429, json={}, headers={"Retry-After": "60"})

    with pytest.raises(RateLimitError) as error:
        requestor.send_request("GET", "campaigns")

    assert error.value.retry_after == 60


def test_retry_after_is_none_when_absent_or_unparsable(requestor, requests_mock):
    requests_mock.get(f"{URL_ROOT}/api/campaigns", status_code=429, json={}, headers={"Retry-After": "Wed, 21 Oct"})

    with pytest.raises(RateLimitError) as error:
        requestor.send_request("GET", "campaigns")

    assert error.value.retry_after is None


def test_non_dict_error_body_is_discarded(requestor, requests_mock):
    requests_mock.get(f"{URL_ROOT}/api/campaigns", status_code=400, json=["rejected"])

    with pytest.raises(APIError) as error:
        requestor.send_request("GET", "campaigns")

    assert error.value.status_code == 400
    assert error.value.body == {}


def test_non_json_error_body_still_raises_api_error(requestor, requests_mock):
    requests_mock.get(f"{URL_ROOT}/api/campaigns", status_code=502, text="<html>bad gateway</html>")

    with pytest.raises(APIError) as error:
        requestor.send_request("GET", "campaigns")

    assert error.value.status_code == 502
    assert error.value.body == {}
