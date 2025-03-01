from mailcoach.resources.base import BaseResource


class CampaignResource(BaseResource):
    """Represent the Campaign resource."""
    endpoint_template = "campaigns"
    required_params = {
        "get_all": [],
        "get": ["uuid"],
        "add": ["data"],
        "update": ["uuid", "data"],
        "remove": ["uuid"],
        "schedule": ["schedule_at", "uuid", "data"]
    }

    def schedule(self, uuid: str, schedule_at: str, data: dict, **kwargs: dict) -> dict:
        kwargs["uuid"] = uuid
        kwargs["schedule_at"] = schedule_at
        kwargs["data"] = data
        self._validate_required_params("schedule", kwargs)

        data["schedule_at"] = schedule_at
        endpoint = f"{self.endpoint_template.format(**kwargs)}/{uuid}"
        response = self.requestor.send_request("PUT", endpoint, data=data)
        return response.get("data", {})
