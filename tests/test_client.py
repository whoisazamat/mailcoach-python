import pytest

from mailcoach.client import MailCoachClient
from mailcoach.helpers.requestor import DEFAULT_TIMEOUT
from mailcoach.resources.campaigns import CampaignResource
from mailcoach.resources.email_lists import EmailListResource
from mailcoach.resources.segments import SegmentResource
from mailcoach.resources.tags import TagResource

from tests.conftest import URL_ROOT


@pytest.fixture
def client():
    with MailCoachClient(token="test-token", url_root=URL_ROOT) as instance:
        yield instance


@pytest.mark.parametrize("attribute, resource", [
    ("email_lists", EmailListResource),
    ("tags", TagResource),
    ("segments", SegmentResource),
    ("campaigns", CampaignResource),
])
def test_client_exposes_resource(client, attribute, resource):
    assert isinstance(getattr(client, attribute), resource)


def test_resources_share_one_requestor(client):
    # A single session means one connection pool and one place holding the token.
    requestors = {id(client.email_lists.requestor), id(client.tags.requestor),
                  id(client.segments.requestor), id(client.campaigns.requestor)}

    assert requestors == {id(client.requestor)}


def test_client_defaults_timeout(client):
    assert client.requestor.timeout == DEFAULT_TIMEOUT


def test_client_forwards_timeout():
    with MailCoachClient(token="test-token", url_root=URL_ROOT, timeout=1.5) as client:
        assert client.requestor.timeout == 1.5


def test_context_manager_closes_the_session(monkeypatch):
    client = MailCoachClient(token="test-token", url_root=URL_ROOT)
    closed = []
    monkeypatch.setattr(client.requestor.session, "close", lambda: closed.append(True))

    with client:
        pass

    assert closed == [True]
