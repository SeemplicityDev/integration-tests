import json
from functools import lru_cache
from typing import Optional

from src.api_client.client import DataAPIServerClient
from utils.ticketing.ticketing_queries import GET_TICKET_MANAGERS_QUERY, GET_ENDPOINT_KEYS_QUERY, \
    GET_QUERY_FIELDS_QUERY, GET_ENDPOINT_FIELDS_QUERY

@lru_cache(maxsize=None)
def get_ticket_managers(client: DataAPIServerClient):
    """
    Get ticket managers
    :param client:
    :return: ticket managers, example:
    [
        {
            "type": "JIRA",
            "providers": [
                {
                    "id": "VGlja2V0UHJvdmlkZXI6MQo=",
                    "is_installed": true
                }
            ]
        },
        {
            "type": "SERVICENOW",
            "providers": [
                {
                    "id": "VGlja2V0UHJvdmlkZXI6Mgo=",
                    "is_installed": true
                }
            ]
        },
    ]
    """
    return client.gql_query(
        jinja_temp=GET_TICKET_MANAGERS_QUERY,
        query_name="ticket_managers",
        variables={"providers_query_context": "CREATE_TICKET"},
    )

@lru_cache(maxsize=None)
def get_ticket_provider(client: DataAPIServerClient, ticket_provider_type: str) -> dict:
    """
    Get ticket provider
    :param client:
    :param ticket_provider_type: "JIRA"/"SERVICENOW"/...
    :return: ticket provider, example:
    {
        "id": "VGlja2V0UHJvdmlkZXI6MQo=",
        "is_installed": true
    }
    """
    ticket_managers = get_ticket_managers(client=client)
    ticket_provider = next((m for m in ticket_managers if m["type"] == ticket_provider_type))
    return ticket_provider["providers"][0]


def get_endpoint_keys(
        client: DataAPIServerClient,
        ticket_provider_id: str,
        selected_keys: dict,
        field_mapping_id: Optional[str] = None
):
    """
    Get endpoint keys
    :param client:
    :param ticket_provider_id: base64 encoded ticket provider id
    :param selected_keys: selected keys, example: {}, {"project": "TEST"}, {"project": "TEST", "issuetype": "Task"}
    :param field_mapping_id: field mapping id
    :return: endpoint keys, example:
    {
        "is_final": true,
        "fields_sections": [
            {
                "rows": [
                    {
                        "fields": [
                            {
                                "field_name": "project",
                                "default_value": {"value": "TEST"},
                                "field_input_type": "SELECT_QUERY",
                                "options": {
                                    "values": [
                                        {
                                            "id": "TEST",
                                            "name": "TEST (Test)"
                                        }
                                    ]
                                }
                            }, {
                                "field_name": "issuetype",
                                "default_value": null,
                                "field_input_type": "SELECT",
                                "options": {
                                    "values": [
                                        {
                                            "id": "Task",
                                            "name": "Task"
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                ]
            }
        ]
    }
    """
    return client.gql_query(
        jinja_temp=GET_ENDPOINT_KEYS_QUERY,
        query_name="endpoint_keys",
        variables={
            "ticket_provider_id": ticket_provider_id,
            "selected_keys": json.dumps(selected_keys).replace('"', '\\"'),
            "field_mapping_id": f'field_mapping_id: "{field_mapping_id}"' if field_mapping_id else "",
        },
    )


def get_query_field_option(
        client: DataAPIServerClient,
        ticket_provider_id: str,
        prefix: str,
        field_name: str
) -> list[dict[str, str]]:
    """
    Get query field option
    :param client:
    :param ticket_provider_id:
    :param prefix:
    :param field_name:
    :return: query field option, example:
    [
        {
            "id": "TEST",
            "name": "TEST (Test)"
        },
        {
            "id": "BLA",
            "name": "BLA (Bla)"
        }
    ]
    """
    return client.gql_query(
        jinja_temp=GET_QUERY_FIELDS_QUERY,
        query_name="get_query_fields",
        variables={
            "ticket_provider_id": ticket_provider_id,
            "field_name": field_name,
            "params": json.dumps({"search_string": prefix}).replace('"', '\\"'),
        },
    )["values"]


def get_endpoint_fields(
        client: DataAPIServerClient,
        ticket_provider_id: str,
        selected_keys: dict,
        filters_config: Optional[str] = None,
        field_mapping_id: Optional[str] = None,
) -> dict:
    return client.gql_query(
        jinja_temp=GET_ENDPOINT_FIELDS_QUERY,
        query_name="endpoint_fields",
        variables={
            "ticket_provider_id": ticket_provider_id,
            "selected_keys": json.dumps(selected_keys).replace('"', '\\"'),
            "field_mapping_id": f'field_mapping_id: "{field_mapping_id}"' if field_mapping_id else "",
            "filters_config": f'filters_config: {filters_config}' if filters_config else "",
        },
    )
