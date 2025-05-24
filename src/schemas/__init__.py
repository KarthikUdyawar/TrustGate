"""Schemas package initializer.

This module defines shared response schemas used throughout the API, including a custom
AppResponse wrapper around FastAPI's JSONResponse for consistent API responses.
"""

from typing import Any, Dict, Optional

from fastapi.responses import JSONResponse


class AppResponse(JSONResponse):  # pylint: disable=too-few-public-methods
    """Custom JSON response wrapper for uniform API responses.

    Attributes:
        body (Any): The main response content.
        message (str): A human-readable message.
        status_code (int): HTTP status code of the response.
        headers (Optional[Dict[str, str]]): Optional HTTP headers.
    """

    def __init__(
        self,
        body: Any = None,
        message: str = "",
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
    ):
        """Initialize the AppResponse with body, message, status code, and optional headers."""
        content = {
            "status_code": status_code,
            "message": message,
            "body": body,
        }
        super().__init__(
            content=content, status_code=status_code, headers=headers
        )
