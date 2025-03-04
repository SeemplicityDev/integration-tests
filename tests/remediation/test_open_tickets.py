import json
from typing import Callable

import pytest

from api_client.client import DataAPIServerClient
from api_client.config import Config
from utils.findings.findings_utils import get_findings
from utils.ticketing.clients.clients import BaseClient
from utils.ticketing.ticketing_queries import MUTATION_OPEN_TICKET


def get_jira_issue_updated_data(external_id: str, required_external_status: str) -> dict:
    return {
        "timestamp": 1611689258458,
        "webhookEvent": "jira:issue_updated",
        "issue_event_type_name": "issue_generic",
        "user": {
            "accountId": "614b224d2a6f5a0071229fb0",
        },
        "issue": {
            "key": external_id,
            "fields": {},
        },
        "changelog": {
            "id": "10360",
            "items": [
                {
                    "field": "status",
                    "fieldtype": "jira",
                    "fieldId": "status",
                    "from": "10001",
                    "fromString": "Backlog",
                    "to": "3",
                    "toString": required_external_status,
                }
            ],
        },
    }


@pytest.mark.parametrize(
    argnames=["value_mapping", "ticket_provider", "finding"],
    argvalues=[
        pytest.param(
            {
                "project": "BLA",
                "issuetype": "Task",
                "summary": "test_title blabla",
                "labels": ["omg"],
                "assignee": "614b224d2a6f5a0071229fb0",
                "description": "test_description",
            },
            "JIRA",
            "test_open_manual_ticket",
            id="jira",
        ),
    ],
    indirect=["ticket_provider", "finding"],
)
@pytest.mark.usefixtures("delete_ticket")
def test_manual_ticket(
        client: DataAPIServerClient,
        ticket_provider_id: str,
        value_mapping: dict,
        finding: dict,
        ticket_client: BaseClient,
        ticket_validator: Callable[[dict, dict], None],
        # jira_webhook_token: str,
        config: Config,
):
    finding_id_int = finding["id_int"]
    ticket = client.gql_query(
        jinja_temp=MUTATION_OPEN_TICKET,
        query_name="open_ticket",
        variables={
            "value_mapping": json.dumps(value_mapping).replace('"', '\\"'),
            "ticket_provider_id": ticket_provider_id,
            "finding_id": finding_id_int,
        }
    )
    external_id_ = ticket["ticket"]["external_id"]
    assert ticket["ticket"]["status"] == "BACKLOG"
    assert ticket["ticket"]["assignee"] == "Shahar Getzovich"

    finding = get_findings(
        client=client,
        filters_config=r'{filtersjson: "{\"field\":\"id\",\"condition\":\"in\",\"value\":[%s]}"}' % finding_id_int,
    )[0]["node"]
    assert finding["tickets"]["edges"][0]["node"]["external_id"] == external_id_
    assert finding["tickets"]["edges"][0]["node"]["status"] == "BACKLOG"
    actual_ticket = ticket_client.get_ticket(external_id=external_id_)
    ticket_validator(actual_ticket, value_mapping)

    # res = requests.post(
    #     f"{config.ticketmaster_url}/jira/issue_updated",
    #     json=get_jira_issue_updated_data(external_id=external_id_, required_external_status="Done"),
    #     headers={"Authorization": f"JWT {jira_webhook_token}"},
    # )
    # assert res.status_code == 200
    # finding = get_findings(
    #     client=client,
    #     filters_config=r'{filtersjson: "{\"field\":\"id\",\"condition\":\"in\",\"value\":[%s]}"}' % finding_id_int,
    # )[0]["node"]
    # assert finding["tickets"]["edges"][0]["node"]["status"] == "DONE"
