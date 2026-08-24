import pytest

import mailcoach


@pytest.mark.parametrize("name", mailcoach.__all__)
def test_every_exported_name_is_importable(name):
    assert getattr(mailcoach, name)


def test_client_is_importable_from_the_package_root():
    with mailcoach.MailCoachClient(token="test-token", url_root="https://mailcoach.test") as client:
        assert client.campaigns is not None


def test_all_is_sorted_and_complete():
    assert mailcoach.__all__ == sorted(mailcoach.__all__)
    assert "MailcoachError" in mailcoach.__all__
