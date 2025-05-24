"""Schemas for role creation, update, and response.

This module defines the Pydantic models for validating role-related request and response data.
"""

import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from models.role import ScopeEnum


class RoleCreateRequest(BaseModel):  # pylint: disable=too-few-public-methods
    """Schema for creating a new role.

    Attributes:
        name (str): The name of the role.
        scopes (Optional[List[ScopeEnum]]): A list of scopes assigned to the role.
    """

    name: str
    scopes: Optional[List[ScopeEnum]] = []

    model_config = ConfigDict(extra="forbid")


class RoleUpdateRequest(BaseModel):  # pylint: disable=too-few-public-methods
    """Schema for updating an existing role.

    Attributes:
        name (Optional[str]): The updated name of the role.
        scopes (Optional[List[ScopeEnum]]): The updated list of scopes.
    """

    name: Optional[str] = None
    scopes: Optional[List[ScopeEnum]] = None

    model_config = ConfigDict(extra="forbid")


class RoleResponse(BaseModel):  # pylint: disable=too-few-public-methods
    """Schema for returning role details in responses.

    Attributes:
        id (UUID): Unique identifier of the role.
        name (str): Name of the role.
        scopes (List[ScopeEnum]): List of scopes assigned to the role.
        created_at (Optional[datetime.datetime]): Timestamp of creation.
        updated_at (Optional[datetime.datetime]): Timestamp of last update.
    """

    id: UUID
    name: str
    scopes: List[ScopeEnum]
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]

    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
    )
