from mailcoach.helpers.requestor import Requestor


class EmailLists:

    def __init__(self, requestor: Requestor):
        self.requestor = requestor

    def get_all(self) -> dict:
        return self.requestor.send_request("GET", "email-lists")
