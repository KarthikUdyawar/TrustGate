"""Module for managing secret storage in HashiCorp Vault."""

from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests
import urllib3
from requests.adapters import HTTPAdapter
from starlette.status import (
    HTTP_200_OK,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_502_BAD_GATEWAY,
    HTTP_503_SERVICE_UNAVAILABLE,
    HTTP_504_GATEWAY_TIMEOUT,
)
from urllib3.exceptions import InsecureRequestWarning
from urllib3.util.retry import Retry

from core.config import get_settings
from core.exceptions import (
    AuthException,
    BadRequestException,
    ForbiddenException,
    InternalServerException,
    NotFoundException,
)
from core.logger import get_logger


@dataclass
class VaultConfig:
    """Holds configuration details for Vault."""

    path_suffix: str
    base_url: str
    role_id: str
    secret_id: str
    reject_unauthorized: bool
    certificate: str


class VaultSession:
    """Handles HTTP requests to Vault with retry logic."""

    def __init__(self, reject_unauthorized: bool, certificate: str) -> None:
        """Initialize a VaultSession.

        Args:
            reject_unauthorized (bool): Whether to reject unauthorized SSL certificates.
            certificate (str): Path to the SSL certificate.
        """
        self.session = self.create_session()
        self.verify = certificate if reject_unauthorized else False

    def create_session(self) -> requests.Session:
        """Creates and configures a requests session with retry logic."""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[
                HTTP_500_INTERNAL_SERVER_ERROR,
                HTTP_502_BAD_GATEWAY,
                HTTP_503_SERVICE_UNAVAILABLE,
                HTTP_504_GATEWAY_TIMEOUT,
            ],
            allowed_methods=["GET", "POST", "DELETE"],
        )
        session.mount("https://", HTTPAdapter(max_retries=retry_strategy))
        session.mount("http://", HTTPAdapter(max_retries=retry_strategy))
        return session

    def check_vault_health(self, base_url: str) -> bool:
        """Checks if Vault is up and running."""
        try:
            response = self.session.get(
                f"{base_url}/v1/sys/health", verify=self.verify
            )
            return response.status_code == HTTP_200_OK
        except requests.RequestException:
            return False


class SecretManager:
    """Manages interactions with HashiCorp Vault for secret management."""

    def __init__(self) -> None:
        """Initialize the SecretManager.

        This sets up logging, configuration, and a Vault session.
        """
        self.logger = get_logger()
        self.settings = get_settings()
        self.vault_config = VaultConfig(**self.settings.get_vault_config())
        self.vault_session = VaultSession(
            self.vault_config.reject_unauthorized,
            self.vault_config.certificate,
        )
        self._token: Optional[str] = None

        # Suppress insecure request warnings if SSL verification is disabled
        if not self.vault_config.reject_unauthorized:
            urllib3.disable_warnings(InsecureRequestWarning)

    def check_vault_health(self) -> bool:
        """Checks if the Vault server is up and running."""
        is_healthy = self.vault_session.check_vault_health(
            self.vault_config.base_url
        )
        if is_healthy:
            self.logger.info("Vault is healthy and running.")
        else:
            self.logger.warning("Vault is not responding.")
        return is_healthy

    def _authenticate(self) -> str:
        """Authenticates with Vault using AppRole."""
        if not all([self.vault_config.role_id, self.vault_config.secret_id]):
            raise BadRequestException("Both role_id and secret_id must be set")

        try:
            response = self.vault_session.session.post(
                f"{self.vault_config.base_url}/v1/auth/approle/login",
                json={
                    "role_id": self.vault_config.role_id,
                    "secret_id": self.vault_config.secret_id,
                },
                verify=self.vault_session.verify,
            )

            if response.status_code == HTTP_401_UNAUTHORIZED:
                raise AuthException("Invalid credentials")

            response.raise_for_status()
            response_data: dict[str, Any] = response.json()
            client_token: str = response_data["auth"]["client_token"]
            return client_token

        except requests.ConnectionError as e:
            self.logger.exception(f"Connection error: {str(e)}")
            raise InternalServerException(f"Connection error: {str(e)}") from e
        except requests.RequestException as e:
            self.logger.exception(f"Authentication request failed: {str(e)}")
            raise InternalServerException(
                f"Authentication request failed: {str(e)}"
            ) from e

    def _ensure_authenticated(self) -> None:
        """Ensures a valid authentication token is available."""
        if not self._token:
            self._token = self._authenticate()

    def _build_path(self, secret_path: str, secret_key: str) -> str:
        """Constructs the full path for a secret in Vault."""
        if not secret_path or not secret_key:
            raise BadRequestException(
                "Both secret_path and secret_key must be provided"
            )
        return f"{secret_path}/{self.vault_config.path_suffix}/{secret_key}"

    def set_secret(
        self, secret_path: str, secret_key: str, secret_data: Dict[str, Any]
    ) -> bool:
        """Stores a secret in Vault."""
        if not secret_data:
            raise BadRequestException("Secret data cannot be empty")

        try:
            self._ensure_authenticated()
            headers = {"X-Vault-Token": self._token}
            full_path = self._build_path(secret_path, secret_key)

            response = self.vault_session.session.post(
                f"{self.vault_config.base_url}/v1/{full_path}",
                json={"data": secret_data},
                headers=headers,
                verify=self.vault_session.verify,
            )

            if response.status_code == HTTP_403_FORBIDDEN:
                raise ForbiddenException("Insufficient permissions")

            response.raise_for_status()
            self.logger.info(f"Secret written successfully at {full_path}")
            return True

        except requests.ConnectionError as e:
            self.logger.exception(f"Connection error: {str(e)}")
            raise InternalServerException(f"Connection error: {str(e)}") from e
        except requests.RequestException as e:
            self.logger.exception(f"Failed to write secret: {str(e)}")
            raise InternalServerException(
                f"Failed to write secret: {str(e)}"
            ) from e

    def get_secret(
        self, secret_path: str, secret_key: str
    ) -> Optional[Dict[str, Any]]:
        """Retrieves a secret from Vault."""
        try:
            self._ensure_authenticated()
            headers = {"X-Vault-Token": self._token}
            full_path = self._build_path(secret_path, secret_key)

            response = self.vault_session.session.get(
                f"{self.vault_config.base_url}/v1/{full_path}",
                headers=headers,
                verify=self.vault_session.verify,
            )

            if response.status_code == HTTP_404_NOT_FOUND:
                self.logger.error(f"Secret not found at {full_path}")
                raise NotFoundException("Secret not found")

            if response.status_code == HTTP_403_FORBIDDEN:
                raise ForbiddenException("Insufficient permissions")

            response.raise_for_status()
            response_data: dict[str, Any] = response.json()
            data: dict[str, Any] = response_data["data"]["data"]
            return data

        except requests.ConnectionError as e:
            self.logger.exception(f"Connection error: {str(e)}")
            raise InternalServerException(f"Connection error: {str(e)}") from e
        except requests.RequestException as e:
            self.logger.exception(f"Failed to read secret: {str(e)}")
            raise InternalServerException(
                f"Failed to read secret: {str(e)}"
            ) from e

    def delete_secret(self, secret_path: str, secret_key: str) -> bool:
        """Deletes a secret from Vault."""
        try:
            self._ensure_authenticated()
            headers = {"X-Vault-Token": self._token}
            full_path = self._build_path(secret_path, secret_key)

            response = self.vault_session.session.delete(
                f"{self.vault_config.base_url}/v1/{full_path}",
                headers=headers,
                verify=self.vault_session.verify,
            )

            if response.status_code == HTTP_404_NOT_FOUND:
                self.logger.error(f"Secret not found at {full_path}")
                raise NotFoundException("Secret not found")

            if response.status_code == HTTP_403_FORBIDDEN:
                raise ForbiddenException("Insufficient permissions")

            response.raise_for_status()
            self.logger.info(f"Secret deleted successfully at {full_path}")
            return True

        except requests.ConnectionError as e:
            self.logger.exception(f"Connection error: {str(e)}")
            raise InternalServerException(f"Connection error: {str(e)}") from e
        except requests.RequestException as e:
            self.logger.exception(f"Failed to delete secret: {str(e)}")
            raise InternalServerException(
                f"Failed to delete secret: {str(e)}"
            ) from e


if __name__ == "__main__":
    try:
        import argparse
        import json
        import sys

        manager: SecretManager = SecretManager()
        logger = get_logger()

        parser = argparse.ArgumentParser(
            description="Secret Management Example"
        )
        parser.add_argument(
            "-o",
            "--operation",
            required=True,
            choices=["write", "read", "delete", "w", "r", "d"],
            help="Operation to perform: write (w), read (r), or delete (d)",
        )
        parser.add_argument(
            "-p", "--path", required=True, help="Vault secret path"
        )
        parser.add_argument(
            "-k", "--key", required=True, help="Vault secret key"
        )
        parser.add_argument(
            "-d",
            "--data",
            help="Vault secret data (required for write operation)",
        )

        args = parser.parse_args()

        secret_path = args.path
        secret_key = args.key
        operation = args.operation

        if operation in ["write", "w"]:
            if not args.data:
                logger.error("Data is required for write operation")
                sys.exit(1)
            secret_data = json.loads(args.data)
            manager.set_secret(secret_path, secret_key, secret_data)
            logger.info("Secret written successfully")

        elif operation in ["read", "r"]:
            retrieved_secret = manager.get_secret(secret_path, secret_key)
            logger.info(f"Retrieved secret: {retrieved_secret}")

        elif operation in ["delete", "d"]:
            manager.delete_secret(secret_path, secret_key)
            logger.info("Secret deleted successfully")

    except (requests.RequestException, InternalServerException) as e:
        logger.exception(f"Error: {str(e)}")
