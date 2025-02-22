from unittest.mock import Mock
import json
import os

import pytest

from mailcoach.resources.email_lists import EmailLists
from mailcoach.helpers.requestor import Requestor


@pytest.fixture
def mock_requestor():
    return Mock(spec=Requestor)


@pytest.fixture
def email_lists(mock_requestor):
    return EmailLists(mock_requestor)


@pytest.fixture
def email_lists_response():
    with open(os.path.join(os.path.dirname(__file__), "test_data", "email_lists.json"), 'r') as file:
        return json.load(file)
