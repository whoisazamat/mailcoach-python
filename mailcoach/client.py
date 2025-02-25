from mailcoach.helpers.requestor import Requestor
from mailcoach.resources.email_lists import EmailList


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
        self.email_lists = EmailList(requestor)
