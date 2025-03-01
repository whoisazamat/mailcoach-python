from mailcoach.resources.base import BaseResource


class EmailListResource(BaseResource):
    """Represent the Email Lists resource."""
    endpoint_template = "email-lists"
    required_params = {
        "get_all": [],
        "get": ["uuid"],
        "add": [],
        "update": ["uuid"],
        "remove": ["uuid"],
    }
