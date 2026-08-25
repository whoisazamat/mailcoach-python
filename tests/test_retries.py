import pytest
import requests

from mailcoach.client import MailCoachClient
from mailcoach.exceptions import APIError, NotFoundError, RateLimitError, RequestError
from mailcoach.transport import DEFAULT_MAX_ATTEMPTS, DEFAULT_MAX_RETRY_WAIT, Requestor
from tests.conftest import URL_ROOT


CAMPAIGNS = f"{URL_ROOT}/api/campaigns"


@pytest.fixture
def slept(monkeypatch):
    """Record the delays instead of waiting them out."""
    recorded: list[float] = []
    monkeypatch.setattr("mailcoach.transport.time.sleep", recorded.append)
    return recorded


@pytest.fixture
def retrying():
    with Requestor(url_root=URL_ROOT, token="test-token", max_attempts=3, max_retry_wait=600) as instance:
        yield instance


def test_rate_limit_is_retried_after_the_header_delay(retrying, requests_mock, slept, sample_response):
    requests_mock.get(CAMPAIGNS, [
        {"status_code": 429, "json": {}, "headers": {"Retry-After": "7"}},
        {"status_code": 200, "json": sample_response},
    ])

    assert retrying.send_request("GET", "campaigns") == sample_response
    assert slept == [7.0]


def test_rate_limit_without_a_header_backs_off_exponentially(retrying, requests_mock, slept, sample_response):
    requests_mock.get(CAMPAIGNS, [
        {"status_code": 429, "json": {}},
        {"status_code": 429, "json": {}},
        {"status_code": 200, "json": sample_response},
    ])

    assert retrying.send_request("GET", "campaigns") == sample_response
    assert slept == [1.0, 2.0]


@pytest.mark.parametrize("status_code", [500, 502, 503, 504])
def test_server_faults_are_retried(retrying, requests_mock, slept, sample_response, status_code):
    requests_mock.get(CAMPAIGNS, [
        {"status_code": status_code, "json": {}},
        {"status_code": 200, "json": sample_response},
    ])

    assert retrying.send_request("GET", "campaigns") == sample_response
    assert slept == [1.0]


def test_connection_errors_are_retried(retrying, requests_mock, slept, sample_response):
    requests_mock.get(CAMPAIGNS, [
        {"exc": requests.exceptions.ConnectTimeout},
        {"status_code": 200, "json": sample_response},
    ])

    assert retrying.send_request("GET", "campaigns") == sample_response
    assert slept == [1.0]


@pytest.mark.parametrize("status_code", [400, 401, 403, 404, 422])
def test_client_errors_are_not_retried(retrying, requests_mock, slept, status_code):
    requests_mock.get(CAMPAIGNS, status_code=status_code, json={})

    with pytest.raises(APIError):
        retrying.send_request("GET", "campaigns")

    assert requests_mock.call_count == 1
    assert slept == []


def test_attempts_are_capped_and_the_original_error_is_reraised(retrying, requests_mock, slept):
    requests_mock.get(CAMPAIGNS, status_code=429, json={"message": "slow down"})

    with pytest.raises(RateLimitError, match="slow down"):
        retrying.send_request("GET", "campaigns")

    assert requests_mock.call_count == 3
    assert slept == [1.0, 2.0]


def test_transport_failure_is_wrapped_once_attempts_run_out(retrying, requests_mock, slept):
    requests_mock.get(CAMPAIGNS, exc=requests.exceptions.ConnectTimeout)

    with pytest.raises(RequestError) as error:
        retrying.send_request("GET", "campaigns")

    assert isinstance(error.value.__cause__, requests.exceptions.RequestException)
    assert requests_mock.call_count == 3
    assert slept == [1.0, 2.0]


def test_total_wait_budget_stops_retrying_early(requests_mock, slept):
    with Requestor(url_root=URL_ROOT, token="test-token", max_attempts=5, max_retry_wait=10) as instance:
        requests_mock.get(CAMPAIGNS, status_code=429, json={}, headers={"Retry-After": "30"})

        with pytest.raises(RateLimitError):
            instance.send_request("GET", "campaigns")

    assert requests_mock.call_count == 1
    assert slept == []


def test_total_wait_budget_accumulates_across_retries(requests_mock, slept):
    # Budget 4s: sleeps of 1s and 2s fit, the third delay of 4s would overshoot 3s already spent.
    with Requestor(url_root=URL_ROOT, token="test-token", max_attempts=5, max_retry_wait=4) as instance:
        requests_mock.get(CAMPAIGNS, status_code=429, json={})

        with pytest.raises(RateLimitError):
            instance.send_request("GET", "campaigns")

    assert requests_mock.call_count == 3
    assert slept == [1.0, 2.0]


def test_retrying_can_be_disabled(requests_mock, slept):
    with Requestor(url_root=URL_ROOT, token="test-token", max_attempts=1) as instance:
        requests_mock.get(CAMPAIGNS, status_code=503, json={})

        with pytest.raises(APIError):
            instance.send_request("GET", "campaigns")

    assert requests_mock.call_count == 1
    assert slept == []


def test_pagination_survives_a_rate_limit_mid_iteration(requests_mock, slept, sample_response):
    second_page = f"{CAMPAIGNS}?page=2"
    requests_mock.get(CAMPAIGNS, json={"data": [sample_response], "links": {"next": second_page}})
    requests_mock.get(second_page, [
        {"status_code": 429, "json": {}, "headers": {"Retry-After": "3"}},
        {"status_code": 200, "json": {"data": [sample_response], "links": {"next": None}}},
    ])

    with MailCoachClient(token="test-token", url_root=URL_ROOT) as client:
        assert list(client.campaigns.get_all()) == [sample_response, sample_response]

    assert slept == [3.0]


def test_max_attempts_below_one_is_rejected():
    with pytest.raises(ValueError, match="max_attempts must be at least 1"):
        Requestor(url_root=URL_ROOT, token="test-token", max_attempts=0)


def test_client_forwards_the_retry_settings():
    with MailCoachClient(token="test-token", url_root=URL_ROOT, max_attempts=7, max_retry_wait=5) as client:
        assert client.requestor.max_attempts == 7
        assert client.requestor.max_retry_wait == 5


def test_client_defaults_the_retry_settings():
    with MailCoachClient(token="test-token", url_root=URL_ROOT) as client:
        assert client.requestor.max_attempts == DEFAULT_MAX_ATTEMPTS
        assert client.requestor.max_retry_wait == DEFAULT_MAX_RETRY_WAIT


def test_a_not_found_still_raises_its_own_type(retrying, requests_mock, slept):
    requests_mock.get(CAMPAIGNS, status_code=404, json={"message": "gone"})

    with pytest.raises(NotFoundError):
        retrying.send_request("GET", "campaigns")

    assert slept == []
