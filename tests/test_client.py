from mailcoach.client import MailCoachClient


def test_client_initialization():
    client = MailCoachClient(token="test_token_123", url_root="https://api.mailcoach.com")

    assert isinstance(client, MailCoachClient)
