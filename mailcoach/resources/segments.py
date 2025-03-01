from mailcoach.resources.base import BaseResource


class SegmentResource(BaseResource):
    """Represent the Segment resource."""
    endpoint_template = "email-lists/{email_list_uuid}/segments"
    required_params = {
        "get_all": ["email_list_uuid"],
        "get": ["uuid", "email_list_uuid"],
        "add": ["data", "email_list_uuid"],
        "update": ["uuid", "data", "email_list_uuid"],
        "remove": ["uuid", "email_list_uuid"],
    }
