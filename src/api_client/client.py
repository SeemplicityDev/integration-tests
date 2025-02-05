import json
from typing import Optional

import boto3
import requests
from jinja2 import Template

from api_client.config import Config
from api_client.token_manager import TokenManager


def get_token_manager(config: Config) -> TokenManager:
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=config.aws_region)

    get_secret_value_response = client.get_secret_value(SecretId=config.cred_secret_name)
    secrets = json.loads(get_secret_value_response.get("SecretString"))
    return TokenManager(
        user_pool_id=secrets["pool_id"],
        client_id=secrets["client_id"],
        username=config.cognito_username,
        password=secrets["admin_password"],
    )


class DataAPIServerClient:
    def __init__(self, url: str, account_uuid: str, token_manager: TokenManager):
        self._url = url
        self._account_uuid = account_uuid
        self._token_manager = token_manager

    @classmethod
    def from_env(cls, account_uuid: Optional[str] = None) -> "DataAPIServerClient":
        config = Config()
        token_manager = get_token_manager(config=config)
        return cls(
            url=config.data_api_server_url,
            account_uuid=account_uuid,
            token_manager=token_manager,
        )

    def execute(self, query: str) -> dict:
        response = requests.post(
            url=self._url,
            json={"query": query},
            headers={
                "X-Account": self._account_uuid,
                "Authorization": f"Bearer {self._token_manager.get_access_token()}",
                "Content-Type": "application/json",
            }
        )
        response.raise_for_status()

        response_data = response.json()
        if 'errors' in response_data:
            raise Exception(f"GraphQL errors: {response_data['errors']}")

        return response_data["data"]

    def gql_query(
            self,
            jinja_temp: Template,
            query_name: Optional[str] = None,
            variables: Optional[dict] = None,
    ) -> dict:
        rendered = jinja_temp.render(**variables) if variables else jinja_temp.render()
        res = self.execute(rendered)
        if query_name:
            return res[query_name]

        return res
