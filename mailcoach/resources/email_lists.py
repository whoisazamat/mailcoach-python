from mailcoach.helpers.base_resource import BaseResource


class EmailLists(BaseResource):

    def get_all(self) -> dict:
        return self.requestor.send_request("GET", "email-lists")
