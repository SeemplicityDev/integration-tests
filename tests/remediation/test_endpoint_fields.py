import json

import pytest

from api_client.client import DataAPIServerClient
from utils.ticketing.ticketing_utils import (
    get_endpoint_fields,
)

@pytest.mark.parametrize(
    argnames=["pre_selected_keys", "expected_fields", "ticket_provider", "finding"],
    argvalues=[
        pytest.param(
            {"project": "BLA", "issuetype": "Task"},
            {
                "assignee": (False, False),
                "components": (False, True),
                "custom_fields": (False, False),
                "description": (False, False),
                "duedate": (False, False),
                "labels": (False, True),
                "priority": (False, True),
                "seemplicity_web_link": (False, False),
                "summary": (True, False)
            },
            "JIRA",
            "test_endpoint_fields",
            id="jira_bla_task",
        ),
    ],
    indirect=["ticket_provider", "finding"]
)
def test_manual_ticket_endpoint_fields(
        pre_selected_keys: dict,
        client: DataAPIServerClient,
        ticket_provider_id: str,
ticket_provider: dict,
        finding: dict,
        expected_fields: dict[str, tuple[bool, bool]],
):
    endpoint_fields = get_endpoint_fields(
        client=client,
        ticket_provider_id=ticket_provider_id,
        selected_keys=pre_selected_keys,
        filters_config=r'{filtersjson: "{\"operator\":\"and\",\"operands\":[{\"field\":\"id\",\"condition\":\"in\",\"value\":[\"%s\"]}]}"}' %
                       finding["id_int"],
    )
    rows = endpoint_fields["fields_sections"][0]["rows"]
    fields = {f["field_name"]: (f["required"], bool(f["options"])) for row in rows for f in row["fields"]}
    assert fields == expected_fields
    title_field = next(f for row in rows for f in row["fields"] if f["field_name"] == "summary")
    assert json.loads(title_field["default_value"])["value"] == f'{finding["title"]} [{finding["resource_name"]}]'


@pytest.mark.parametrize(
    argnames=["remediation_queue", "value_mapping", "ticket_provider"],
    argvalues=[
        pytest.param(
            {
                "title": "test_queue",
                "max_concurrent_opened_tickets": 2,
                "state": "ENABLED",
                "filters_config": r'{scopesid: "U2NvcGVHcm91cDox", filtersid: "RmluZGluZ0ZpbHRlcjoxCg=="}',
                "value_mapping": {
                    "project": "BLA",
                    "issuetype": "Task",
                    "summary": "test_title {{finding.title}} [{{resource.name}}]",
                    "labels": ["omg"],
                    "assignee": "614b224d2a6f5a0071229fb0",
                    "description": "test_description {{finding.description}}",
                    "duedate": "{{finding.duedate}}"
                },
            },
            {
                "summary": "test_title {{finding.title}} [{{resource.name}}]",
                "labels": ["omg"],
                "assignee": "614b224d2a6f5a0071229fb0",
                "description": "test_description {{finding.description}}",
                "duedate": "{{finding.duedate}}"
            },
            "JIRA",
            id="jira_bla_task",
        ),
    ],
    indirect=["remediation_queue", "ticket_provider"]
)
def test_field_mapping_queue_ticket_endpoint_fields(
        client: DataAPIServerClient,
        field_mapping_id: str,
        ticket_provider_id: str,
        value_mapping: dict,
):
    endpoint_fields = get_endpoint_fields(
        client=client,
        ticket_provider_id=ticket_provider_id,
        selected_keys={},
        filters_config=None,
        field_mapping_id=field_mapping_id,
    )
    rows = endpoint_fields["fields_sections"][0]["rows"]
    fields = {f["field_name"]: json.loads(f["default_value"])["value"] for row in rows for f in row["fields"] if
              f["default_value"]}
    assert fields == value_mapping
    title_field = next(f for row in rows for f in row["fields"] if f["field_name"] == "summary")
    assert json.loads(title_field["default_value"])["value"] == "test_title {{finding.title}} [{{resource.name}}]"
