import pytest
import requests

from mailcoach.exceptions import APIError, RequestError
from mailcoach.helpers.requestor import Requestor

from tests.conftest import URL_ROOT


@pytest.mark.parametrize("path, expected", [
    ("campaigns", f"{URL_ROOT}/api/campaigns"),
    ("/campaigns", f"{URL_ROOT}/api/campaigns"),
    ("email-lists/test-email-list-uuid/tags", f"{URL_ROOT}/api/email-lists/test-email-list-uuid/tags"),
    (f"{URL_ROOT}/api/campaigns?page=2", f"{URL_ROOT}/api/campaigns?page=2"),
])
def test_build_url(requestor, path, expected):
    assert requestor._build_url(path) == expected


def test_build_url_refuses_another_host(requestor):
    with pytest.raises(RequestError, match="Refusing to follow URL"):
        requestor._build_url("https://attacker.test/api/campaigns")


def test_send_request_returns_decoded_body(requestor, requests_mock, sample_response):
    requests_mock.get(f"{URL_ROOT}/api/campaigns", json=sample_response)

    assert requestor.send_request("GET", "campaigns") == sample_response


def test_send_request_sends_bearer_token_and_timeout(requestor, requests_mock):
    requests_mock.get(f"{URL_ROOT}/api/campaigns", json={})

    requestor.send_request("GET", "campaigns")

    assert requests_mock.last_request.headers["Authorization"] == "Bearer test-token"
    assert requests_mock.last_request.timeout == requestor.timeout


def test_send_request_sends_payload_as_json(requestor, requests_mock, sample_data):
    requests_mock.post(f"{URL_ROOT}/api/campaigns", json={}, status_code=201)

    requestor.send_request("POST", "campaigns", data=sample_data)

    assert requests_mock.last_request.json() == sample_data


@pytest.mark.parametrize("status_code", [200, 201, 202])
def test_send_request_accepts_any_success_status(requestor, requests_mock, sample_response, status_code):
    requests_mock.post(f"{URL_ROOT}/api/campaigns", json=sample_response, status_code=status_code)

    assert requestor.send_request("POST", "campaigns", data={}) == sample_response


def test_send_request_returns_empty_dict_for_empty_body(requestor, requests_mock):
    requests_mock.delete(f"{URL_ROOT}/api/campaigns/test-uuid", status_code=204)

    assert requestor.send_request("DELETE", "campaigns/test-uuid") == {}


@pytest.mark.parametrize("status_code", [400, 401, 404, 422, 429, 500])
def test_send_request_raises_on_error_status(requestor, requests_mock, status_code):
    requests_mock.get(f"{URL_ROOT}/api/campaigns", status_code=status_code, text="denied")

    with pytest.raises(APIError, match=f"Unexpected response {status_code}: denied"):
        requestor.send_request("GET", "campaigns")


def test_send_request_wraps_and_chains_transport_failure(requestor, requests_mock):
    requests_mock.get(f"{URL_ROOT}/api/campaigns", exc=requests.exceptions.ConnectTimeout)

    with pytest.raises(RequestError) as error:
        requestor.send_request("GET", "campaigns")

    assert isinstance(error.value.__cause__, requests.exceptions.RequestException)


def test_send_request_raises_on_malformed_json(requestor, requests_mock):
    requests_mock.get(f"{URL_ROOT}/api/campaigns", text="<html>gateway</html>")

    with pytest.raises(RequestError, match="Malformed JSON"):
        requestor.send_request("GET", "campaigns")


def test_close_is_idempotent():
    requestor = Requestor(url_root=URL_ROOT, token="test-token")

    requestor.close()
    requestor.close()
