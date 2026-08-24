import pytest

from mailcoach.client import MailCoachClient
from mailcoach.resources.automations import AutomationMailResource, AutomationResource
from mailcoach.resources.campaigns import CampaignResource
from mailcoach.resources.email_lists import EmailListResource
from mailcoach.resources.subscribers import SubscriberResource
from mailcoach.resources.tags import TagResource
from mailcoach.resources.templates import TemplateResource
from mailcoach.resources.transactional import TransactionalMailResource, TransactionalMailTemplateResource
from mailcoach.transport import DEFAULT_TIMEOUT
from tests.conftest import URL_ROOT


@pytest.fixture
def client():
    with MailCoachClient(token="test-token", url_root=URL_ROOT) as instance:
        yield instance


@pytest.mark.parametrize(("attribute", "resource"), [
    ("email_lists", EmailListResource),
    ("tags", TagResource),
    ("campaigns", CampaignResource),
    ("subscribers", SubscriberResource),
    ("templates", TemplateResource),
    ("automation_mails", AutomationMailResource),
    ("automations", AutomationResource),
    ("transactional_mails", TransactionalMailResource),
    ("transactional_mail_templates", TransactionalMailTemplateResource),
])
def test_client_exposes_resource(client, attribute, resource):
    assert isinstance(getattr(client, attribute), resource)


def test_resources_share_one_requestor(client):
    # A single session means one connection pool and one place holding the token.
    requestors = {id(client.email_lists.requestor), id(client.tags.requestor),
                  id(client.campaigns.requestor),
                  id(client.subscribers.requestor), id(client.templates.requestor),
                  id(client.automation_mails.requestor), id(client.automations.requestor),
                  id(client.transactional_mails.requestor), id(client.transactional_mail_templates.requestor)}

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
