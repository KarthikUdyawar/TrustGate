"""Initialize the models package."""

from core.db import Base
from models.role import Role, ScopeEnum

__all__ = ["Base", "Role", "ScopeEnum"]
