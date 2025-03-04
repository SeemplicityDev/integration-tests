import os

import pytest
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import Session, sessionmaker
import boto3
from boto3.dynamodb.conditions import Key

from api_client.client import DataAPIServerClient
from api_client.config import Config

# Define test directories with their corresponding CLI flags
TEST_DIRECTORIES = {
    "remediation": "tests/remediation/",
}
os.environ["AWS_PROFILE"] = "development"
os.environ["AWS_ENDPOINT_URL_DYNAMODB"] = "http://localhost:8900"


def pytest_addoption(parser):
    for option in TEST_DIRECTORIES:
        parser.addoption(
            f"--{option}",
            action="store_true",
            help=f"Run tests in '{TEST_DIRECTORIES[option]}'"
        )


def pytest_collection_modifyitems(config, items):
    # Collect all enabled flags
    enabled_dirs = [
        path for option, path in TEST_DIRECTORIES.items()
        if config.getoption(f"--{option}")
    ]

    # If no flags are provided, run all tests
    if not enabled_dirs:
        return

    # Filter items based on enabled directories
    items[:] = [
        item for item in items
        if any(dir_path in str(item.fspath) for dir_path in enabled_dirs)
    ]


@pytest.fixture(scope="session")
def account_uuid(config: Config) -> str:
    customer_schema = config.customer_schema

    resource = boto3.resource("dynamodb")
    accounts_table = resource.Table("account")
    response = accounts_table.scan(
        Select="ALL_ATTRIBUTES",
        FilterExpression=Key("database_schema").eq(customer_schema)
    )
    items = response.get("Items", [])
    if not items:
        raise ValueError(f"No account found for schema: {customer_schema}")

    return items[0]["uuid"]

@pytest.fixture(scope="session")
def client(account_uuid: str) -> DataAPIServerClient:
    return DataAPIServerClient.from_env(account_uuid=account_uuid)


@pytest.fixture(scope="session")
def config() -> Config:
    return Config()


@pytest.fixture(scope="session")
def postgres_session(config: Config) -> Session:
    engine = create_engine(config.postgres_url)
    engine.execution_options(schema_translate_map={None: config.customer_schema})
    with engine.connect() as conn:
        session_factory = sessionmaker()
        session = session_factory(bind=conn)
        yield session
        session.close()
