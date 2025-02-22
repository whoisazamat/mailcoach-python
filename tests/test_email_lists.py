def test_email_lists_get_all(email_lists, email_lists_response, mock_requestor):
    mock_requestor.send_request.return_value = email_lists_response
    response = email_lists.get_all()
    assert response == email_lists_response
