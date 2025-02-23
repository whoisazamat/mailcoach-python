def test_email_lists_get_all(email_lists, mock_requestor):
    mock_requestor.send_request.side_effect = [
        {
            "data": [{"uuid": 1, "name": "List 1"}],
            "links": {"next": "email-lists?page=2"},
        },
        {
            "data": [{"uuid": 2, "name": "List 2"}],
            "links": {"next": None},
        },
    ]

    results = list(email_lists.get_all())
    expected_calls = [
        ("GET", "email-lists"),
        ("GET", "email-lists?page=2"),
    ]
    actual_calls = [(args[0], args[1]) for args, _ in mock_requestor.send_request.call_args_list]

    assert actual_calls == expected_calls
    assert results == [{"uuid": 1, "name": "List 1"}, {"uuid": 2, "name": "List 2"}]


def test_email_lists_get(email_lists, mock_requestor):
    expected_response = {"data": [{"uuid": 1, "name": "List 1"}]}
    mock_requestor.send_request.return_value = expected_response
    response = email_lists.get(uuid="4a0c4c34-9a82-4746-bfeb-e45a7a38526b")
    assert response[0] == expected_response["data"][0]


def test_email_lists_add(email_lists, mock_requestor):
    expected_response = {"data": {"uuid": 1, "name": "List 1"}}
    mock_requestor.send_request.return_value = expected_response
    response = email_lists.add({"uuid": 1, "name": "List 1"})
    assert response == expected_response["data"]


def test_email_lists_update(email_lists, mock_requestor):
    expected_response = {"data": {"uuid": 1, "name": "List 1"}}
    mock_requestor.send_request.return_value = expected_response
    response = email_lists.update(uuid="4a0c4c34-9a82-4746-bfeb-e45a7a38526b", data={"uuid": 1, "name": "List 1"})
    assert response == expected_response["data"]
