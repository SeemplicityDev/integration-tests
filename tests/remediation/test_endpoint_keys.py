import json

import pytest

from api_client.client import DataAPIServerClient
from utils.ticketing.ticketing_utils import get_query_field_option, get_endpoint_keys
from tests.remediation.fixtures import (
    ticket_provider_id,  # NOQA F401
    field_mapping_id,  # NOQA F401
    remediation_queue,  # NOQA F401
    ticket_provider,  # NOQA F401
)


@pytest.mark.parametrize(
    argnames=["pre_selected_keys", "fields_to_query", "ticket_provider"],
    argvalues=[
        pytest.param(
            {"seemplicity_type": "catalog", "seemplicity_catalog_item_id": "3e85765347269110f7ae3238436d43af"},
            {"seemplicity_catalog_item_id": "seem"},
            "SERVICENOW",
            id="servicenow_seemplicity_catalog",
        ),
        pytest.param(
            {"project": "BLA", "issuetype": "Task"},
            {},
            "JIRA",
            id="jira_bla_task",
        ),
    ],
    indirect=["ticket_provider"]
)
def test_manual_ticket_endpoint_keys(
        pre_selected_keys: dict,
        client: DataAPIServerClient,
        ticket_provider_id: str,
        fields_to_query: dict[str, str],
):
    endpoint_keys = get_endpoint_keys(
        client=client,
        ticket_provider_id=ticket_provider_id,
        selected_keys={},
    )
    assert not endpoint_keys["is_final"]
    rounds, selected_keys = 0, {}
    while not endpoint_keys["is_final"] and rounds < len(pre_selected_keys) + 1:
        rounds += 1
        rows = endpoint_keys["fields_sections"][0]["rows"]
        field = next((f for row in rows for f in row["fields"] if f["field_name"] not in selected_keys))
        field_name = field["field_name"]
        if not field["options"] or not field["options"]["values"]:
            raise Exception(f"got no options for key field {field_name}: {field}")

        pre_selected_id = pre_selected_keys[field_name]
        if field_name in fields_to_query:
            assert field["field_input_type"] == "SELECT_QUERY"
            key_field_prefix = fields_to_query[field_name]
            query_field_option = get_query_field_option(
                client=client,
                ticket_provider_id=ticket_provider_id,
                field_name=field_name,
                prefix=key_field_prefix
            )
            selected_key_id = next((p["id"] for p in query_field_option if p["id"] == pre_selected_id))

        else:
            selected_key_id = next((p["id"] for p in field["options"]["values"] if p["id"] == pre_selected_id))

        selected_keys[field_name] = selected_key_id
        endpoint_keys = get_endpoint_keys(
            client=client,
            ticket_provider_id=ticket_provider_id,
            selected_keys=selected_keys,
        )

    assert endpoint_keys["is_final"]
    assert selected_keys == pre_selected_keys

@pytest.mark.parametrize(
    argnames=["pre_selected_keys", "remediation_queue", "ticket_provider"],
    argvalues=[
        pytest.param(
            {"project": "BLA", "issuetype": "Task"},
            {
                "title": "test_queue",
                "max_concurrent_opened_tickets": 2,
                "state": "ENABLED",
                "filters_config": r'{scopesid: "U2NvcGVHcm91cDox", filtersid: "RmluZGluZ0ZpbHRlcjoxCg=="}',
                "value_mapping": {"project": "BLA", "issuetype": "Task", "summary": "test summary"},
            },
            "JIRA",
            id="jira_bla_task",
        ),
    ],
    indirect=["remediation_queue", "ticket_provider"]
)
def test_remediation_queue_ticket_endpoint_keys(
        pre_selected_keys: dict,
        client: DataAPIServerClient,
        field_mapping_id: str,
        ticket_provider_id: str,
):
    endpoint_keys = get_endpoint_keys(
        client=client,
        ticket_provider_id=ticket_provider_id,
        selected_keys={},
        field_mapping_id=field_mapping_id,
    )
    assert endpoint_keys["is_final"]
    rows = endpoint_keys["fields_sections"][0]["rows"]
    fields = [f for row in rows for f in row["fields"] if f["field_name"] in pre_selected_keys]
    default_values = {f["field_name"]: json.loads(f["default_value"])["value"] for f in fields}
    assert default_values == pre_selected_keys
