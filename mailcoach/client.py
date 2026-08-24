from types import TracebackType
from typing import Self

from mailcoach.helpers.requestor import DEFAULT_TIMEOUT, Requestor
from mailcoach.resources.campaigns import CampaignResource
from mailcoach.resources.email_lists import EmailListResource
from mailcoach.resources.segments import SegmentResource
from mailcoach.resources.subscribers import SubscriberResource
from mailcoach.resources.tags import TagResource


class MailCoachClient:
    """Entry point to the Mailcoach API, exposing one attribute per resource."""

    def __init__(self, token: str, url_root: str, timeout: float = DEFAULT_TIMEOUT) -> None:
        self.requestor = Requestor(url_root=url_root, token=token, timeout=timeout)

        self.email_lists = EmailListResource(self.requestor)
        self.tags = TagResource(self.requestor)
        self.segments = SegmentResource(self.requestor)
        self.campaigns = CampaignResource(self.requestor)
        self.subscribers = SubscriberResource(self.requestor)

    def close(self) -> None:
        """Release the underlying connection pool."""
        self.requestor.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()
