from collections.abc import Generator

from mailcoach.helpers.base_resource import BaseResource


class EmailLists(BaseResource):

    def get_all(self) -> Generator[dict, None, None]:
        return self.iter_all("email-lists")

    def get(self, uuid: str) -> dict:
        return self.get_specific_item(
            endpoint="email-lists",
            uuid=uuid,
        )

    def add(self, email_list_data: dict) -> dict:
        return self.add_item(
            endpoint="email-lists",
            data=email_list_data,
        )

    def update(self, uuid: str, data: dict) -> dict:
        return self.update_item(
            endpoint="email-lists",
            uuid=uuid,
            data=data,
        )
