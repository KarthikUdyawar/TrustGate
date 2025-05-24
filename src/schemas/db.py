"""Defines common database query parameter schemas.

This module contains Pydantic models for filtering, pagination, and sorting of data queries.
"""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from constants import DEFAULT_LIMIT


class ReadAllParams(BaseModel):  # pylint: disable=too-few-public-methods
    """Parameters for retrieving multiple records from the database with optional filtering and \
    pagination.

    Attributes:
        filters (Optional[Dict[str, Any]]): Dictionary of filtering conditions.
        limit (Optional[int]): Maximum number of records to return. Defaults to DEFAULT_LIMIT.
        offset (Optional[int]): Number of records to skip. Useful for pagination.
        order_by (Optional[str]): Field name to sort the results by.
        desc_order (Optional[bool]): Whether to sort in descending order.
        show_all (Optional[bool]): Whether to show all records (ignores pagination).
    """

    filters: Optional[Dict[str, Any]] = None
    limit: Optional[int] = Field(default=DEFAULT_LIMIT, ge=1)
    offset: Optional[int] = Field(default=None, ge=0)
    order_by: Optional[str] = None
    desc_order: Optional[bool] = False
    show_all: Optional[bool] = False
