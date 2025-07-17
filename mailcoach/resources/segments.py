from mailcoach.resources.base import BaseResource


class SegmentResource(BaseResource):
    """Represent the Segment resource."""

    endpoint_template = "email-lists/{email_list_uuid}/segments"
