from types import TracebackType
from typing import Self

from mailcoach.helpers.requestor import DEFAULT_TIMEOUT, Requestor
from mailcoach.resources.automations import AutomationMailResource, AutomationResource
from mailcoach.resources.campaigns import CampaignResource
from mailcoach.resources.email_lists import EmailListResource
from mailcoach.resources.subscribers import SubscriberResource
from mailcoach.resources.tags import TagResource
from mailcoach.resources.templates import TemplateResource
from mailcoach.resources.transactional import TransactionalMailResource, TransactionalMailTemplateResource


class MailCoachClient:
    """Entry point to the Mailcoach API, exposing one attribute per resource."""

    def __init__(self, token: str, url_root: str, timeout: float = DEFAULT_TIMEOUT) -> None:
        self.requestor = Requestor(url_root=url_root, token=token, timeout=timeout)

        self.email_lists = EmailListResource(self.requestor)
        self.tags = TagResource(self.requestor)
        self.campaigns = CampaignResource(self.requestor)
        self.subscribers = SubscriberResource(self.requestor)
        self.templates = TemplateResource(self.requestor)
        self.automation_mails = AutomationMailResource(self.requestor)
        self.automations = AutomationResource(self.requestor)
        self.transactional_mails = TransactionalMailResource(self.requestor)
        self.transactional_mail_templates = TransactionalMailTemplateResource(self.requestor)

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
