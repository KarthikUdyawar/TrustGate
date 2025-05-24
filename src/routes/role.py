"""Role Routes.

This module defines the FastAPI routes for managing roles, including creation, retrieval,
update, deletion, and listing of all roles. These routes interact with the RoleController
to perform database operations.
"""

from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from controllers.role import RoleController
from core.db import get_db
from schemas import AppResponse
from schemas.role import RoleCreateRequest, RoleUpdateRequest

router = APIRouter()


@router.post("/roles", response_class=JSONResponse)
def create_role(
    role_data: RoleCreateRequest, db: Session = Depends(get_db)
) -> AppResponse:
    """Create a new role.

    Args:
        role_data (RoleCreateRequest): The data required to create a role.
        db (Session): SQLAlchemy session dependency.

    Returns:
        JSONResponse: The created role's data.
    """
    controller = RoleController(db)
    return controller.create_role(role_data)


@router.get("/roles/{role_id}", response_class=JSONResponse)
def get_role(role_id: UUID, db: Session = Depends(get_db)) -> AppResponse:
    """Retrieve a role by its ID.

    Args:
        role_id (UUID): The ID of the role to retrieve.
        db (Session): SQLAlchemy session dependency.

    Returns:
        JSONResponse: The role data.
    """
    controller = RoleController(db)
    return controller.get_role(role_id)


@router.get("/roles", response_class=JSONResponse)
def get_all_roles(db: Session = Depends(get_db)) -> AppResponse:
    """Retrieve all roles.

    Args:
        db (Session): SQLAlchemy session dependency.

    Returns:
        JSONResponse: List of all roles.
    """
    controller = RoleController(db)
    return controller.get_all_roles()


@router.put("/roles/{role_id}", response_class=JSONResponse)
def update_role(
    role_id: UUID, role_data: RoleUpdateRequest, db: Session = Depends(get_db)
) -> AppResponse:
    """Update a role by ID.

    Args:
        role_id (UUID): The ID of the role to update.
        role_data (RoleUpdateRequest): The updated role data.
        db (Session): SQLAlchemy session dependency.

    Returns:
        JSONResponse: The updated role data.
    """
    controller = RoleController(db)
    return controller.update_role(role_id, role_data)


@router.delete("/roles/{role_id}", response_class=JSONResponse)
def delete_role(
    role_id: UUID, hard_delete: bool = False, db: Session = Depends(get_db)
) -> AppResponse:
    """Delete a role by ID.

    Args:
        role_id (UUID): The ID of the role to delete.
        hard_delete (bool): If True, permanently delete the role. Otherwise, soft delete.
        db (Session): SQLAlchemy session dependency.

    Returns:
        JSONResponse: Result of the deletion operation.
    """
    controller = RoleController(db)
    return controller.delete_role(role_id, hard_delete)
