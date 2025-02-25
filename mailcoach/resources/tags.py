from typing import Generator

from mailcoach.helpers.base_resource import BaseResource


class Tag(BaseResource):

    def get_all(self, email_list_uuid: str) -> Generator[dict, None, None]:
        return self.iter_all(
            f"email-lists/{email_list_uuid}/tags",
        )

    def get(self, email_list_uuid: str, uuid: str) -> dict:
        return self.get_specific_item(
            endpoint=f"email-lists/{email_list_uuid}/tags",
            uuid=uuid,
        )

    def add(self, email_list_uuid: str, data: dict) -> dict:
        return self.add_item(
            endpoint=f"email-lists/{email_list_uuid}/tags",
            data=data,
        )

    def update(self, email_list_uuid: str, uuid: str, data: dict) -> dict:
        return self.update_item(
            endpoint=f"email-lists/{email_list_uuid}/tags",
            uuid=uuid,
            data=data,
        )

    def remove(self, email_list_uuid: str, uuid: str) -> dict:
        return self.delete_item(
            endpoint=f"email-lists/{email_list_uuid}/tags",
            uuid=uuid,
        )
