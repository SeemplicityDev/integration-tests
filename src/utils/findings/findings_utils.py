from typing import Optional

from src.api_client.client import DataAPIServerClient
from utils.findings.findings_queries import GET_PLAIN_FINDINGS_QUERY


def get_findings(client: DataAPIServerClient, filters_config: Optional[str] = None) -> list[dict[str, dict]]:
    return client.gql_query(
        jinja_temp=GET_PLAIN_FINDINGS_QUERY,
        query_name="findings",
        variables={"filters_config": f" ( filters_config: {filters_config} ) " if filters_config else ""},
    )["edges"]
