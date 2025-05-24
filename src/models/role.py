"""Models definition for roles using ScopeEnum directly.

This module contains the SQLAlchemy models for managing roles and their associated scopes.
"""

import uuid
from enum import Enum
from typing import Any

from sqlalchemy import ARRAY, Boolean, Column, DateTime, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from core.db import Base


class ScopeEnum(str, Enum):
    """Defines the available permission scopes for a role."""

    READ_GLOBAL = "read:global"
    WRITE_GLOBAL = "write:global"
    DELETE_GLOBAL = "delete:global"
    READ_TENANT = "read:tenant"
    WRITE_TENANT = "write:tenant"
    DELETE_TENANT = "delete:tenant"
    READ_PROJECT = "read:project"
    WRITE_PROJECT = "write:project"
    DELETE_PROJECT = "delete:project"
    READ_CLIENT = "read:client"
    WRITE_CLIENT = "write:client"
    DELETE_CLIENT = "delete:client"
    # Add more as needed


class Role(Base):  # type: ignore
    """Represents a role in the system, associated with multiple scopes.

    Attributes:
        id: Unique identifier of the role.
        name: Name of the role.
        scopes: List of permission scopes associated with the role.
        is_deleted: Soft-delete flag.
        created_at: Timestamp of creation.
        updated_at: Timestamp of last update.
    """

    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False)
    scopes = Column(ARRAY(String), nullable=False, default=[])  # type: ignore
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (Index("ix_roles_is_deleted", "is_deleted"),)

    def __repr__(self) -> str:
        """Return a string representation of the role object."""
        return f"<Role {self.id} ({self.name})>"

    def to_dict(self) -> dict[str, Any]:
        """Convert the role object to a dictionary.

        Returns:
            dict: Dictionary containing role attributes.
        """
        return {
            "id": str(self.id),
            "name": self.name,
            "scopes": self.scopes,
            "is_deleted": self.is_deleted,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def add_scope(self, scope: ScopeEnum) -> None:
        """Add a scope to the role if it's not already present.

        Args:
            scope (ScopeEnum): The scope to be added.
        """
        if scope.value not in self.scopes:
            self.scopes.append(scope.value)

    def remove_scope(self, scope: ScopeEnum) -> None:
        """Remove a scope from the role if it exists.

        Args:
            scope (ScopeEnum): The scope to be removed.
        """
        if scope.value in self.scopes:
            self.scopes.remove(scope.value)
