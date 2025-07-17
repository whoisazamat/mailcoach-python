from mailcoach.helpers.requestor import Requestor
from mailcoach.resources.campaigns import CampaignResource
from mailcoach.resources.email_lists import EmailListResource
from mailcoach.resources.segments import SegmentResource
from mailcoach.resources.tags import TagResource


class MailCoachClient:
    def __init__(self, token: str, url_root: str):
        requestor = Requestor(
            url_root=url_root,
            token=token,
            request_headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {token}",
            },
        )
        self.email_lists = EmailListResource(requestor)
        self.tags = TagResource(requestor)
        self.segments = SegmentResource(requestor)
        self.campaigns = CampaignResource(requestor)
