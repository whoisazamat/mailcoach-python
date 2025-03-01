from mailcoach.client import MailCoachClient
from mailcoach.resources.email_lists import EmailListResource
from mailcoach.resources.tags import TagResource
from mailcoach.resources.segments import SegmentResource


def test_client_initialization():
    client = MailCoachClient(token="test_token_123", url_root="https://api.mailcoach.com")
    assert isinstance(client, MailCoachClient)
    assert isinstance(client.email_lists, EmailListResource)
    assert isinstance(client.tags, TagResource)
    assert isinstance(client.segments, SegmentResource)
