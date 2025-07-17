from mailcoach.resources.base import BaseResource


class CampaignResource(BaseResource):
    """Represent the Campaign resource."""

    endpoint_template = "campaigns"

    def schedule(self, uuid: str, schedule_at: str, data: dict) -> dict:
        data["schedule_at"] = schedule_at
        endpoint = f"{self.endpoint_template}/{uuid}"
        response = self.requestor.send_request("PUT", endpoint, data=data)
        return response.get("data", {})

    def send_test(self, uuid: str, email_list: list[str]) -> None:
        endpoint = f"{self.endpoint_template}/{uuid}/send_test"
        data = {"email": ",".join(email_list)}
        self.requestor.send_request("POST", endpoint, data)

    def send(self, uuid: str) -> None:
        endpoint = f"{self.endpoint_template}/{uuid}/send"
        self.requestor.send_request("POST", endpoint)

    def opens(self, uuid: str) -> dict:
        endpoint = f"{self.endpoint_template}/{uuid}/opens"
        response = self.requestor.send_request("GET", endpoint)
        return response.get("data", {})

    def click(self, uuid: str) -> dict:
        endpoint = f"{self.endpoint_template}/{uuid}/click"
        response = self.requestor.send_request("GET", endpoint)
        return response.get("data", {})

    def unsubscribes(self, uuid: str) -> dict:
        endpoint = f"{self.endpoint_template}/{uuid}/unsubscribes"
        response = self.requestor.send_request("GET", endpoint)
        return response.get("data", {})

    def bounces(self, uuid: str) -> dict:
        endpoint = f"{self.endpoint_template}/{uuid}/unsubscribes"
        response = self.requestor.send_request("GET", endpoint)
        return response.get("data", {})
