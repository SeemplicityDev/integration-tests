import json
from typing import Callable

import boto3
import pytest
from atlassian_jwt import encode
from sqlalchemy import text
from sqlalchemy.orm import Session

from api_client.client import DataAPIServerClient
from api_client.config import Config
from utils.findings.findings_utils import get_findings
from utils.ticketing.remediation_queries import CREATE_REMEDIATION_QUEUE, DELETE_REMEDIATION_QUEUE
from utils.ticketing.ticketing_utils import get_ticket_provider
from utils.ticketing.clients.clients import BaseClient
from utils.ticketing.clients import jira


def jira_webhook_token(account_uuid: str, ticket_provider: dict):
    resource = boto3.resource("dynamodb")
    identifiers_table = resource.Table("identifier")
    external_identifier = ticket_provider["external_identifier"]
    identifiers_table.put_item(
        Item={
            "identifier": external_identifier,
            "type": "JIRA_CLIENT_KEY",
            "account": account_uuid,
        }
    )
    return encode.encode_token(
        "POST", "/jira/issue_updated", external_identifier, ticket_provider["oauth_client_id"]
    )


@pytest.fixture
def remediation_queue(client: DataAPIServerClient, request, ticket_provider_id: str) -> dict:
    queue_params = request.param
    value_mapping = json.dumps(queue_params.pop("value_mapping")).replace('"', '\\"')
    queue = client.gql_query(
        jinja_temp=CREATE_REMEDIATION_QUEUE,
        query_name="create_remediation_queue",
        variables={**queue_params, "ticket_provider_id": ticket_provider_id, "value_mapping": value_mapping},
    )["remediation_queue"]
    _remediation_queue_id = queue["id"]

    yield queue

    client.gql_query(
        jinja_temp=DELETE_REMEDIATION_QUEUE,
        query_name="delete_remediation_queue",
        variables={"id": _remediation_queue_id},
    )


@pytest.fixture
def remediation_queue_id(remediation_queue: dict) -> str:
    return remediation_queue["id"]


@pytest.fixture
def field_mapping_id(remediation_queue: dict) -> str:
    return remediation_queue["field_mapping"]["id"]


@pytest.fixture(scope="session")
def ticket_provider(client: DataAPIServerClient, request) -> dict:
    return get_ticket_provider(
        client=client,
        ticket_provider_type=request.param,
    )


@pytest.fixture
def ticket_provider_id(ticket_provider: dict) -> str:
    return ticket_provider["id"]


@pytest.fixture
def finding_without_ticket(client: DataAPIServerClient) -> dict:
    return get_findings(
        client=client,
        filters_config=r'{filtersjson: "{\"field\":\"ticket_status\",\"condition\":\"not_in\",\"value\":[\"BACKLOG\", \"IN_PROGRESS\", \"SCHEDULED\", \"DONE\", \"REJECTED\"]}"}'
    )[0]["node"]


@pytest.fixture
def finding(client: DataAPIServerClient, request) -> dict:
    title = request.param
    return get_findings(
        client=client,
        filters_config=fr'{{filtersjson: "{{\"field\":\"title\",\"condition\":\"likelist\",\"value\":[\"{title}\"]}}"}}'
    )[0]["node"]


@pytest.fixture
def ticket_client(ticket_provider: dict, config: Config) -> BaseClient:
    ticket_provider_type_ = ticket_provider["type"]
    provider_type_to_client_generator = {
        "JIRA": jira.get_client,
    }
    return provider_type_to_client_generator[ticket_provider_type_](**config.dict())


@pytest.fixture
def ticket_validator(ticket_provider: dict) -> Callable[[dict, dict], None]:
    ticket_provider_type_ = ticket_provider["type"]
    provider_type_to_validator = {
        "JIRA": jira.validate_ticket_fields,
    }
    return provider_type_to_validator[ticket_provider_type_]


@pytest.fixture
def delete_ticket(ticket_client: BaseClient, finding: dict, postgres_session: Session, config: Config):
    finding_id_int = finding["id_int"]

    yield
    query = f"""
        SELECT id, external_id FROM {config.customer_schema}.tickets
        where id = (
            SELECT ticket_id FROM {config.customer_schema}.finding_ticket_associations WHERE finding_id = {finding_id_int}
        )
    """
    ticket_external_ids = postgres_session.execute(text(query)).first()
    if ticket_external_ids:
        _id, ticket_external_id = ticket_external_ids[0], ticket_external_ids[1]
        try:
            ticket_client.delete_ticket(external_id=ticket_external_id)
        except Exception as e:
            print(f"Failed to delete ticket with external_id={ticket_external_id}, error: {e}")
        postgres_session.execute(text(f"DELETE FROM {config.customer_schema}.tickets where id = {_id}"))
        postgres_session.execute(
            text(f"DELETE FROM {config.customer_schema}.finding_ticket_associations where ticket_id = {_id}"))
        postgres_session.execute(
            text(f"DELETE FROM {config.customer_schema}.tickets_remediation_data where ticket_id = {_id}"))
        postgres_session.commit()
