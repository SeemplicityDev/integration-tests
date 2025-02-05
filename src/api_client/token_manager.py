import base64
import json
import time
from typing import Any, Dict

from pycognito import Cognito


class TokenManager:
    def __init__(self, user_pool_id: str, client_id: str, username: str, password: str):
        self._cognito = Cognito(
            user_pool_id=user_pool_id,
            client_id=client_id,
            username=username,
        )
        self._password = password

        self._access_token = None
        self._refresh_token = None
        self._expires_at = 0

    def get_access_token(self) -> str:
        """
        Returns a valid access token, refreshing or generating a new one if needed.
        """
        current_time = int(time.time())

        if self._access_token and current_time < self._expires_at:
            return self._access_token  # Token is still valid

        if self._refresh_token:
            self._refresh_access_token()
            return self._access_token

        self._create_access_token()
        return self._access_token

    def _create_access_token(self) -> None:
        """Authenticate and create a new access token."""
        self._cognito.authenticate(password=self._password)
        self._refresh_token = self._cognito.refresh_token
        self._update_token_data(self._cognito.access_token)

    def _refresh_access_token(self) -> None:
        """Refresh the access token using the existing refresh token."""
        self._cognito.refresh_token = self._refresh_token
        self._cognito.renew_access_token()
        self._update_token_data(self._cognito.access_token)

    def _update_token_data(self, token: str) -> None:
        """Update the access token and its expiration timestamp."""
        payload = decode_access_token(token)
        self._access_token = token
        self._expires_at = payload.get("exp", 0)


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decodes a JWT access token without verifying the signature.

    Args:
        token (str): The JWT token to decode.

    Returns:
        Dict[str, Any]: The decoded token payload.
    """
    try:
        payload_encoded = token.split(".")[1]
        # Add Base64 padding if needed
        padding = "=" * (-len(payload_encoded) % 4)
        payload_encoded += padding

        payload_json = base64.urlsafe_b64decode(payload_encoded).decode("utf-8")
        return json.loads(payload_json)

    except (IndexError, ValueError, json.JSONDecodeError) as e:
        raise ValueError(f"Invalid token: {e}")
