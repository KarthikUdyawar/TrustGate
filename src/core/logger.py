"""
Logging setup module using Loguru.

This module contains a `LoggerSetup` class that configures the Loguru logger
for multiple destinations including console outputs and rotating files.
"""

import sys
from typing import Any

import yaml
from loguru import logger


class LoggerSetup:
    """
    A class to configure and manage logging using the Loguru library.

    The logger is configured to output logs to multiple destinations:
      - `sys.stderr` for error-level logs and above.
      - `sys.stdout` for debug and info-level logs.
      - Rotating files for errors, general application logs, and API-specific logs.
    """

    def __init__(self, config_path: str = "src/constants/logging.yaml") -> None:
        """
        Initializes the LoggerSetup instance and sets up logging configuration.

        Args:
            config_path (str): Path to the YAML configuration file for logging.
        """
        self.config_path = config_path
        self.setup_logging()

    def setup_logging(self) -> None:
        """
        Configures the Loguru logger based on the YAML configuration file.

        The configuration specifies multiple handlers and their respective
        settings, including log levels, formats, and rotation policies.
        """
        logger.remove()  # Remove the default logger

        config = self.load_config()

        for handler in config.get("handlers", []):
             # Convert string-based sinks to actual objects
            sink = handler["sink"]
            if sink == "sys.stdout":
                sink = sys.stdout

            # Only apply file-related parameters if sink is a file
            kwargs = {}
            if isinstance(sink, str) and not sink.startswith("sys."):
                kwargs["rotation"] = handler.get("rotation")
                kwargs["retention"] = handler.get("retention")
                kwargs["compression"] = handler.get("compression")

            logger.add(
                sink,
                level=handler.get("level", "INFO"),
                format=handler.get("format", "{message}"),
                colorize=handler.get("colorize", False),
                serialize=handler.get("serialize", False),
                **kwargs  # Only include file-related parameters for file sinks
            )

        # logger.add(sys.stdout, level="INFO")
        logger.info("Logging configured with Loguru")

    def load_config(self) -> Any:
        """
        Loads configuration from a YAML file.

        Returns:
            dict: The parsed configuration.

        Raises:
            FileNotFoundError: If the configuration file does not exist.
            yaml.YAMLError: If there is an error in parsing the YAML file.
        """
        try:
            with open(self.config_path, encoding="utf-8") as file:
                return yaml.safe_load(file)
        except FileNotFoundError as e:
            logger.error("Configuration file not found: %s", self.config_path)
            raise e
        except yaml.YAMLError as e:
            logger.error("Error parsing Configuration file: %s", e)
            raise e
        

if __name__ == "__main__":
    logger_setup = LoggerSetup()
    logger.debug("Debug test message")
    logger.info("Info test message")
    logger.warning("Warning test message")
    logger.error("Error test message")
    logger.critical("Critical test message")

    try:
        raise ValueError("Test exception")
    except ValueError as e:
        logger.exception(e)
