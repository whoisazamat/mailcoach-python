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
