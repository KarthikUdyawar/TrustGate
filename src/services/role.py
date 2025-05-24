"""Service layer for role management.

This module contains business logic for creating, retrieving, updating,
and deleting roles. It communicates with the database via a custom Database class.
"""

from enum import Enum
from typing import List, cast
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from core.db import Database
from core.exceptions import (
    BadRequestException,
    ConflictException,
    NotFoundException,
)
from models.role import Role
from schemas.role import RoleCreateRequest, RoleResponse, RoleUpdateRequest


class RoleService:
    """Service class for role-related operations.

    Provides methods to create, retrieve, update, and delete roles using the
    injected database session.
    """

    def __init__(self, db_session: Session):
        """Initialize RoleService with a database session.

        Args:
            db_session (Session): SQLAlchemy database session.
        """
        self.db = Database(db_session)

    def create_role(self, role_data: RoleCreateRequest) -> RoleResponse:
        """Create a new role in the database.

        Args:
            role_data (RoleCreateRequest): Data for the new role.

        Returns:
            RoleResponse: Created role data.

        Raises:
            ConflictException: If a role with the same name already exists.
            BadRequestException: If the creation fails.
        """
        existing_role = self.db.read(Role, {"name": role_data.name})
        if existing_role:
            raise ConflictException(
                detail="Role with this name already exists."
            )

        data = role_data.model_dump()

        if "scopes" in data and data["scopes"]:
            data["scopes"] = [
                scope.value if isinstance(scope, Enum) else scope
                for scope in data["scopes"]
            ]

        new_role = self.db.create(Role, data)
        if not new_role:
            raise BadRequestException(detail="Failed to create role.")

        role_pydantic = RoleResponse.model_validate(new_role).model_dump()
        return jsonable_encoder(role_pydantic)

    def get_role(self, role_id: UUID) -> RoleResponse:
        """Retrieve a role by its ID.

        Args:
            role_id (UUID): Unique identifier of the role.

        Returns:
            RoleResponse: Retrieved role data.

        Raises:
            NotFoundException: If the role does not exist.
        """
        role = self.db.read(Role, {"id": role_id})
        if not role:
            raise NotFoundException(detail="Role not found.")

        role_pydantic = RoleResponse.model_validate(role).model_dump()
        return jsonable_encoder(role_pydantic)

    def get_all_roles(self) -> List[RoleResponse]:
        """Retrieve all roles from the database.

        Returns:
            List[RoleResponse]: List of all roles.
        """
        roles = self.db.read_all(Role)
        roles_pydantic = [RoleResponse.model_validate(role) for role in roles]
        # return jsonable_encoder([role.model_dump() for role in roles_pydantic])
        serialized = [role.model_dump() for role in roles_pydantic]
        return cast(List[RoleResponse], jsonable_encoder(serialized))

    def update_role(
        self, role_id: UUID, role_data: RoleUpdateRequest
    ) -> RoleResponse:
        """Update an existing role by ID.

        Args:
            role_id (UUID): Unique identifier of the role.
            role_data (RoleUpdateRequest): Updated role data.

        Returns:
            RoleResponse: Updated role data.

        Raises:
            NotFoundException: If the role is not found or update fails.
        """
        data = role_data.model_dump(exclude_unset=True)

        if "scopes" in data and data["scopes"]:
            data["scopes"] = [
                scope.value if isinstance(scope, Enum) else scope
                for scope in data["scopes"]
            ]

        updated_role = self.db.update(Role, role_id, data)
        if not updated_role:
            raise NotFoundException(
                detail="Role not found or failed to update."
            )

        role_pydantic = RoleResponse.model_validate(updated_role).model_dump()
        return jsonable_encoder(role_pydantic)

    def delete_role(self, role_id: UUID, hard_delete: bool = False) -> bool:
        """Delete a role by ID.

        Args:
            role_id (UUID): Unique identifier of the role.
            hard_delete (bool): Whether to perform a hard delete.

        Returns:
            bool: True if deletion was successful.

        Raises:
            NotFoundException: If the role does not exist or deletion fails.
        """
        deleted: bool = self.db.delete(Role, role_id, hard_delete=hard_delete)
        if not deleted:
            raise NotFoundException(
                detail="Role not found or failed to delete."
            )

        return deleted
