import os
from typing import Optional
from pydantic import BaseSettings


class Config(BaseSettings):
    env: str = os.getenv("ENV", "dev")
    postgres_url: str = os.getenv("POSTGRES_URL", "postgresql://postgres:Password1!@localhost:5432/postgres")
    data_api_server_url: Optional[str] = os.getenv("DATA_API_SERVER_URL", "http://localhost:5050/api/graphql")
    ticketmaster_url: str = os.getenv("TICKETMASTER_URL", "http://localhost:3000/ticketmaster")

    customer_schema: str = os.getenv("CUSTOMER_SCHEMA", "seemplicitydemo")
    customer_secret_key: str = os.getenv("CUSTOMER_SECRET_KEY", "SEEM")
    user_email: str = os.getenv("USER_EMAIL", "cypress@seemplicity.io")
    cognito_username: Optional[str] = os.getenv("COGNITO_USERNAME", "cypress@seemplicity.io")
    cognito_pool_id: Optional[str] = os.getenv("COGNITO_POOL_ID")
    cred_secret_name: str = os.getenv("CRED_SECRET_NAME", "automation/env/development")
    aws_region: str = os.getenv("AWS_REGION", "eu-central-1")

    jira_url: str = os.getenv("JIRA_URL", "testing-env.atlassian.net")
    jira_external_identifier: str = os.getenv("JIRA_EXTERNAL_IDENTIFIER", "87d53fe9-5730-397f-9a57-48f5285a26b4")

    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "env_setup", "local", ".env.local-data-api-server")
        env_file_encoding = 'utf-8'
