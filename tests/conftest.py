from unittest.mock import MagicMock

import pytest

from mailcoach.helpers.requestor import Requestor


@pytest.fixture
def mock_requestor():
    """Fixture to create a mocked Requestor."""
    return MagicMock(spec=Requestor)


@pytest.fixture
def sample_response():
    """Fixture for a sample API response."""
    return {"data": {"uuid": "123", "name": "Test"}}


@pytest.fixture
def sample_data():
    """Fixture for sample data."""
    return {"name": "updated name"}
