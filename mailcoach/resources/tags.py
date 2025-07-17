from mailcoach.resources.base import BaseResource


class TagResource(BaseResource):
    """Represent the Tag resource."""

    endpoint_template = "email-lists/{email_list_uuid}/tags"
