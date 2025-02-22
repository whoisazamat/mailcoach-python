from collections.abc import Generator

from mailcoach.helpers.base_resource import BaseResource


class EmailLists(BaseResource):

    def get_all(self) -> Generator[dict, None, None]:
        return self.iter_all("email-lists")
