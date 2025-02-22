from mailcoach.helpers.requestor import Requestor


class BaseResource:
    def __init__(self, requestor: Requestor):
        self.requestor = requestor
