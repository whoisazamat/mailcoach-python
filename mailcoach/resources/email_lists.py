from collections.abc import Generator

from mailcoach.helpers.base_resource import BaseResource


class EmailLists(BaseResource):

    def get_all(self) -> Generator[dict, None, None]:
        return self.iter_all("email-lists")

    def get(self, uuid: str) -> dict:
        response = self.requestor.send_request(
            method="GET",
            url=f"/email-lists/{uuid}",
        )
        return response["data"]
