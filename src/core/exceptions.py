"""Custom exceptions for the application.

This module defines a set of custom exceptions that extend FastAPI's `HTTPException`.
Each exception represents a specific HTTP error status and provides a meaningful
error message to the client.
"""

from fastapi import HTTPException
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_500_INTERNAL_SERVER_ERROR,
)


class CustomException(HTTPException):
    """Base class for custom HTTP exceptions."""

    def __init__(self, status_code: int, detail: str):
        """Initialize a custom exception with status code and detail message.

        Args:
            status_code (int): The HTTP status code.
            detail (str): A descriptive error message.
        """
        super().__init__(status_code=status_code, detail=detail)


class AuthException(CustomException):
    """Exception raised for authentication failures (401 Unauthorized)."""

    def __init__(self, detail: str = "Authentication failed"):
        """Initialize an authentication exception.

        Args:
            detail (str): The error message (default: "Authentication failed").
        """
        super().__init__(status_code=HTTP_401_UNAUTHORIZED, detail=detail)


class NotFoundException(CustomException):
    """Exception raised when a requested resource is not found (404 Not Found)."""

    def __init__(self, detail: str = "Resource not found"):
        """Initialize a not found exception.

        Args:
            detail (str): The error message (default: "Resource not found").
        """
        super().__init__(status_code=HTTP_404_NOT_FOUND, detail=detail)


class BadRequestException(CustomException):
    """Exception raised for bad requests (400 Bad Request)."""

    def __init__(self, detail: str = "Bad request"):
        """Initialize a bad request exception.

        Args:
            detail (str): The error message (default: "Bad request").
        """
        super().__init__(status_code=HTTP_400_BAD_REQUEST, detail=detail)


class ForbiddenException(CustomException):
    """Exception raised when access is forbidden (403 Forbidden)."""

    def __init__(self, detail: str = "Access forbidden"):
        """Initialize a forbidden exception.

        Args:
            detail (str): The error message (default: "Access forbidden").
        """
        super().__init__(status_code=HTTP_403_FORBIDDEN, detail=detail)


class ConflictException(CustomException):
    """Exception raised when a conflict occurs (409 Conflict)."""

    def __init__(self, detail: str = "Conflict occurred"):
        """Initialize a conflict exception.

        Args:
            detail (str): The error message (default: "Conflict occurred").
        """
        super().__init__(status_code=HTTP_409_CONFLICT, detail=detail)


class UnprocessableEntityException(CustomException):
    """Exception raised for unprocessable entity errors (422 Unprocessable Entity)."""

    def __init__(self, detail: str = "Unprocessable entity"):
        """Initialize an unprocessable entity exception.

        Args:
            detail (str): The error message (default: "Unprocessable entity").
        """
        super().__init__(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY, detail=detail
        )


class InternalServerException(CustomException):
    """Exception raised for internal server errors (500 Internal Server Error)."""

    def __init__(self, detail: str = "Internal server error"):
        """Initialize an internal server error exception.

        Args:
            detail (str): The error message (default: "Internal server error").
        """
        super().__init__(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=detail
        )
