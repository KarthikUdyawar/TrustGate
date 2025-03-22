"""Configuration settings for the TrustGate application.

This module defines the core configuration settings for the TrustGate application using
Pydantic's BaseSettings for type-safe environment variable management and validation.
"""

from functools import lru_cache
from typing import Any, Dict

from pydantic_settings import BaseSettings

from core.logger import get_logger


class Settings(BaseSettings):
    """Configuration settings for the TrustGate application.

    This class encapsulates all application-wide settings, providing default values
    and methods to access configuration state. Settings can be overridden via environment
    variables or a .env file.

    Attributes:
        APP_NAME (str): The name of the application. Defaults to "TrustGate".
        VERSION (str): The application version number. Defaults to "0.1.0".
        MODE (str): The operating mode of the application. Defaults to "development".
    """

    # Application settings
    APP_NAME: str = "TrustGate"
    VERSION: str = "0.1.0"
    MODE: str = "development"

    VAULT_KV_VERSION: int = 2
    VAULT_PROTOCOL: str = "https"
    VAULT_HOST: str = "localhost"
    VAULT_PORT: int = 8200
    VAULT_REJECT_UNAUTHORIZED: bool = False
    VAULT_CERTIFICATE: str = "/path/to/cert.pem"
    VAULT_ROLE_ID: str = "my-role-id"
    VAULT_SECRET_ID: str = "my-secret-id"

    def is_development(self) -> bool:
        """Check if the application is running in development mode.

        Returns:
            bool: True if MODE is set to "development", False otherwise.
        """
        return self.MODE == "development"

    def get_app_version(self) -> str:
        """Get the formatted application version string.

        Returns:
            str: The version prefixed with 'v' (e.g., "v0.1.0").
        """
        return f"v{self.VERSION}"

    def get_vault_config(self) -> Dict[str, Any]:
        """Retrieve Vault configuration details.

        Returns:
            Dict[str, Any]: A dictionary containing Vault configuration parameters.
        """
        return {
            "path_suffix": "data" if self.VAULT_KV_VERSION > 1 else "",
            "base_url": f"{self.VAULT_PROTOCOL}://{self.VAULT_HOST}:{self.VAULT_PORT}",
            "reject_unauthorized": self.VAULT_REJECT_UNAUTHORIZED,
            "certificate": self.VAULT_CERTIFICATE,
            "role_id": self.VAULT_ROLE_ID,
            "secret_id": self.VAULT_SECRET_ID,
        }

    class Config:  # pylint: disable=too-few-public-methods
        """Configuration for Pydantic settings.

        Defines how Pydantic should handle environment variables and file loading.

        Attributes:
            env_file (str): The name of the environment file to load (".env").
            case_sensitive (bool): Whether environment variable names are case-sensitive (False).
        """

        env_file = ".env"
        case_sensitive = False


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Retrieve and cache the application settings.

    This function uses lru_cache to memoize the Settings instance, preventing
    repeated file reads or environment variable parsing on subsequent calls.

    Returns:
        Settings: An instance of the Settings class with loaded configuration.
    """
    return Settings()


if __name__ == "__main__":
    # Example usage of the settings
    log = get_logger()
    settings = get_settings()
    log.info(settings.is_development())  # Prints whether in development mode
    log.info(settings.get_app_version())  # Prints the formatted version string
    log.info(settings.get_vault_config())
