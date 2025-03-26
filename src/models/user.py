"""User model definition.

This module contains the SQLAlchemy model for the 'users' table.
"""

from typing import Any

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.sql import func

from core.db import Base


class User(Base):  # type: ignore
    """Represents a user in the system."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_deleted = Column(Boolean, default=False, index=True)  # default is False

    def __repr__(self) -> str:
        """Return a string representation of the User object."""
        return f"<User {self.id} ({self.user_name})>"

    def to_dict(self) -> dict[str, Any]:
        """Return user data as a dictionary (excluding sensitive data)."""
        return {
            "id": self.id,
            "user_name": self.user_name,
            "email": self.email,
            "created_at": self.created_at,
            "is_deleted": self.is_deleted,
        }
