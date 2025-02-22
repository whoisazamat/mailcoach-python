def test_email_lists_get_all(email_lists, mock_requestor):
    mock_requestor.send_request.side_effect = [
        {
            "data": [{"uid": 1, "name": "List 1"}],
            "links": {"next": "email-lists?page=2"},
        },
        {
            "data": [{"uid": 2, "name": "List 2"}],
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
    assert results == [{"uid": 1, "name": "List 1"}, {"uid": 2, "name": "List 2"}]
