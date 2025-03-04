import json
from typing import Optional

import boto3


def get_secret(secret_name: str, aws_region: Optional[str] = "eu-central-1") -> dict:
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=aws_region)
    secret = client.get_secret_value(SecretId=secret_name)
    return json.loads(secret.get("SecretString"))
