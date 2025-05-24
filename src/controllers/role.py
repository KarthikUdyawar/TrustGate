"""Controller for role-related operations."""

from uuid import UUID

# from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

from schemas import AppResponse
from schemas.role import RoleCreateRequest, RoleUpdateRequest
from services.role import RoleService


class RoleController:
    """Handles HTTP requests related to role operations."""

    def __init__(self, db_session: Session):
        """Initialize the RoleController with a database session."""
        self.service = RoleService(db_session)

    def create_role(self, role_data: RoleCreateRequest) -> AppResponse:
        """Create a new role."""
        new_role = self.service.create_role(role_data)
        return AppResponse(
            body=new_role,
            message="Role created successfully.",
            status_code=HTTP_201_CREATED,
        )

    def get_role(self, role_id: UUID) -> AppResponse:
        """Retrieve a role by its ID."""
        role = self.service.get_role(role_id)
        return AppResponse(
            body=role,
            message="Role fetched successfully.",
            status_code=HTTP_200_OK,
        )

    def get_all_roles(self) -> AppResponse:
        """Retrieve all roles."""
        roles = self.service.get_all_roles()
        return AppResponse(
            body=roles,
            message="Roles fetched successfully.",
            status_code=HTTP_200_OK,
        )

    def update_role(
        self, role_id: UUID, role_data: RoleUpdateRequest
    ) -> AppResponse:
        """Update a role with the given ID."""
        updated_role = self.service.update_role(role_id, role_data)
        return AppResponse(
            body=updated_role,
            message="Role updated successfully.",
            status_code=HTTP_200_OK,
        )

    def delete_role(
        self, role_id: UUID, hard_delete: bool = False
    ) -> AppResponse:
        """Delete a role, soft or hard depending on the flag."""
        deleted = self.service.delete_role(role_id, hard_delete=hard_delete)
        return AppResponse(
            body={"delete_status": deleted, "is_hard_delete": hard_delete},
            message="Role deleted successfully.",
            status_code=HTTP_200_OK,
        )
