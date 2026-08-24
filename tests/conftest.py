from unittest.mock import MagicMock

import pytest

from mailcoach.helpers.requestor import Requestor


URL_ROOT = "https://mailcoach.test"
UUID = "test-uuid"
EMAIL_LIST_UUID = "test-email-list-uuid"


@pytest.fixture
def mock_requestor():
    """Fixture to create a mocked Requestor."""
    return MagicMock(spec=Requestor)


@pytest.fixture
def requestor():
    """Fixture for a real Requestor, to be driven by requests_mock."""
    with Requestor(url_root=f"{URL_ROOT}/", token="test-token") as instance:
        yield instance


@pytest.fixture
def sample_response():
    """Fixture for a sample API response."""
    return {"data": {"uuid": "123", "name": "Test"}}


@pytest.fixture
def sample_data():
    """Fixture for sample data."""
    return {"name": "updated name"}
