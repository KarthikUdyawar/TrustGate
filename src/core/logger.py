"""Logging setup module using Loguru.

This module provides a `LoggerSetup` class to configure the Loguru logger for flexible
and customizable logging. It supports multiple output destinations, including console
(sys.stdout) and rotating log files, with settings loaded from a YAML configuration file.
"""

import sys
from typing import Any

import yaml
from loguru import logger


class LoggerSetup:
    """A class to configure and manage logging using the Loguru library.

    The logger is configured to direct logs to multiple sinks based on a YAML configuration,
    such as console output (sys.stdout) and rotating files for errors, general logs,
    and API-specific logs. It supports customizable log levels, formats, and file rotation policies.

    Attributes:
        config_path (str): Path to the YAML configuration file.
    """

    def __init__(
        self, config_path: str = "src/constants/logging.yaml"
    ) -> None:
        """Initialize the LoggerSetup instance and configure logging.

        Args:
            config_path (str): Path to the YAML configuration file for logging.
                Defaults to "src/constants/logging.yaml".
        """
        self.config_path = config_path
        self.setup_logging()

    def setup_logging(self) -> None:
        """Configure the Loguru logger using settings from the YAML configuration file.

        This method removes the default Loguru logger and sets up new handlers as defined
        in the configuration file. Handlers can include console output and file sinks with
        options like log level, format, rotation, retention, and compression.

        The configuration is expected to provide a list of handlers with their settings.
        """
        logger.remove()  # Remove the default logger

        config = self.load_config()

        for handler in config.get("handlers", []):
            # Convert string-based sinks to actual objects
            sink = handler["sink"]
            if sink == "sys.stdout":
                sink = sys.stdout

            # Only apply file-related parameters if sink is a file path
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
                **kwargs,  # File-specific parameters only for file sinks
            )

        logger.info("Logging configured with Loguru")

    def load_config(self) -> Any:
        """Load logging configuration from a YAML file.

        Reads and parses the YAML file specified by `config_path` to provide the logging
        configuration as a dictionary.

        Returns:
            dict: The parsed configuration dictionary containing handler settings.

        Raises:
            FileNotFoundError: If the specified YAML configuration file is not found.
            yaml.YAMLError: If the YAML file contains invalid syntax or structure.
        """
        try:
            with open(self.config_path, encoding="utf-8") as file:
                return yaml.safe_load(file)
        except FileNotFoundError as e:
            logger.error("Configuration file not found: %s", self.config_path)
            raise e
        except yaml.YAMLError as e:
            logger.error("Error parsing configuration file: %s", e)
            raise e


if __name__ == "__main__":
    # Example usage of the LoggerSetup class
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
