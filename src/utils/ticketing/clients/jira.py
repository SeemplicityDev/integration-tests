import requests
from typing import Optional

from atlassian_jwt import encode

from utils.aws_utils import get_secret
from utils.ticketing.clients.clients import BaseClient


class JiraClient(BaseClient):
    def __init__(self, jira_url: str, atlassian_connect_app_key: str, jira_secret_key: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = jira_url
        self.atlassian_connect_app_key = atlassian_connect_app_key
        self.secret_key = jira_secret_key

    def _get_headers(self, uri: str, method: Optional[str] = "GET") -> dict:
        return {"Accept": "application/json", "Authorization": self._get_authorization(uri=uri, method=method)}

    def get_ticket(self, external_id: str) -> dict:
        uri = f"rest/api/3/issue/{external_id}"
        return requests.get(
            f"https://{self.base_url}/{uri}", headers=self._get_headers(uri=uri)
        ).json()

    def delete_ticket(self, external_id: str):
        uri = f"rest/api/3/issue/{external_id}"
        res = requests.get(
            f"https://{self.base_url}/{uri}", headers=self._get_headers(uri=uri, method="DELETE")
        )
        assert res.ok, f"failed to delete ticket: {res.text}"

    def _get_authorization(self, uri: str, method: str) -> str:
        token = encode.encode_token(http_method=method, url=uri, clientKey=self.atlassian_connect_app_key,
                                    sharedSecret=self.secret_key)
        return f"JWT {token}"


def get_client(jira_url: str, jira_external_identifier: str, customer_secret_key: str, *args, **kwargs) -> JiraClient:
    customer_secret = get_secret(secret_name=customer_secret_key)
    secret = customer_secret["ticket_providers"][f"jira_{jira_external_identifier}"]
    return JiraClient(
        jira_url=jira_url,
        jira_secret_key=secret,
        atlassian_connect_app_key="seemplicity-app",
    )


def validate_ticket_fields(ticket: dict, fields_to_validate: dict):
    for field in fields_to_validate:
        if field == "project":
            assert ticket["fields"]["project"]["key"] == fields_to_validate["project"]
        elif field == "issuetype":
            assert ticket["fields"]["issuetype"]["name"] == fields_to_validate["issuetype"]
        elif field == "summary":
            assert ticket["fields"]["summary"] == fields_to_validate["summary"]
        elif field == "labels":
            assert ticket["fields"]["labels"] == fields_to_validate["labels"]
        elif field == "assignee":
            assert ticket["fields"]["assignee"]["accountId"] == fields_to_validate["assignee"]
