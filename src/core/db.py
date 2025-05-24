"""Database configuration module."""

from typing import Any, Dict, Generator, List, Optional, Type, TypeVar, Union

from sqlalchemy import asc, create_engine, desc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeMeta, Session, sessionmaker

from core.config import get_settings
from core.logger import get_logger
from schemas import db

settings = get_settings()
logger = get_logger()

# Create engine
engine = create_engine(
    settings.get_db_url(),
    pool_pre_ping=True,  # Enable automatic reconnection
    pool_size=5,  # Set pool size
    max_overflow=10,  # Set max overflow
)

# Create SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base
Base = declarative_base()


# Dependency to get DB session
def get_db() -> Generator[Session, None, None]:
    """Yields a database session.

    This function provides a database session using SQLAlchemy's sessionmaker.
    It ensures the session is properly closed after use.

    Returns:
        Generator yielding a SQLAlchemy Session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Enhanced Database Utility Class
# T = TypeVar("T", bound=BaseModel)
# T = TypeVar("T", bound=Base) # type: ignore
T = TypeVar("T", bound=DeclarativeMeta)


class Database:
    """A utility class to perform common CRUD operations using SQLAlchemy ORM \
        with logging and soft delete support."""

    def __init__(self, db_session: Session):
        """Initialize an Database class."""
        self.db_session = db_session

    def _get_unique_fields(self, model: Type[T]) -> List[str]:
        """Automatically extract column names that have unique=True."""
        return [
            column.name
            for column in model.__table__.columns  # type: ignore[attr-defined]
            if column.unique and not column.primary_key
        ]

    def create(self, model: Type[T], data: Dict[str, Any]) -> Union[T, None]:
        """Create a new record or reactivate an existing soft-deleted record."""
        try:
            unique_fields = self._get_unique_fields(model)
            existing = None

            if unique_fields:
                filters = {
                    field: data[field]
                    for field in unique_fields
                    if field in data
                }
                if filters:
                    existing = (
                        self.db_session.query(model)
                        .filter_by(**filters)
                        .first()
                    )

            if existing:
                if getattr(existing, "is_deleted", False):
                    for key, value in data.items():
                        setattr(existing, key, value)
                    existing.is_deleted = False
                    self.db_session.commit()
                    self.db_session.refresh(existing)
                    logger.debug(f"Reactivated {model.__name__}: {existing}")
                    return existing

                logger.warning(
                    f"{model.__name__} with {filters} already exists and is active."
                )
                return None

            db_obj = model(**data)
            self.db_session.add(db_obj)
            self.db_session.commit()
            self.db_session.refresh(db_obj)
            logger.debug(f"Successfully created {model.__name__}: {db_obj}")
            return db_obj

        except SQLAlchemyError as e:
            self.db_session.rollback()
            logger.error(f"Failed to create {model.__name__}: {e}")
            return None

    def read(
        self, model: Type[T], filters: Dict[str, Any], show_all: bool = False
    ) -> Union[T, None]:
        """Read a single record by filters."""
        try:
            query = self.db_session.query(model).filter_by(**filters)
            if not show_all and hasattr(model, "is_deleted"):
                query = query.filter_by(is_deleted=False)

            result = query.first()
            if result:
                logger.debug(f"Successfully read {model.__name__}: {result}")
            else:
                logger.warning(
                    f"No record found for {model.__name__} with filters {filters}"
                )
            return result
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logger.error(
                f"Failed to read {model.__name__} with filters {filters}: {e}"
            )
            return None

    def read_all(
        self,
        model: Type[T],
        params: Optional[db.ReadAllParams] = None,
    ) -> List[T]:
        """Read all records using ReadAllParams."""
        try:
            query = self.db_session.query(model)

            if params is not None:
                if not params.show_all and hasattr(model, "is_deleted"):
                    query = query.filter_by(is_deleted=False)

                if params.filters:
                    query = query.filter_by(**params.filters)
                if params.order_by:
                    query = query.order_by(
                        desc(params.order_by)
                        if params.desc_order
                        else asc(params.order_by)
                    )
                if params.limit:
                    query = query.limit(params.limit)
                if params.offset:
                    query = query.offset(params.offset)

            results = query.all()
            logger.debug(
                f"Successfully read all {model.__name__}: {len(results)} records found"
            )
            return results
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logger.error(f"Failed to read all {model.__name__}: {e}")
            return []

    def update(
        self, model: Type[T], obj_id: Any, update_data: Dict[str, Any]
    ) -> Union[T, None]:
        """Update an existing record by ID."""
        try:
            obj = self.read(model, {"id": obj_id})
            if not obj:
                logger.warning(
                    f"{model.__name__} with id {obj_id} not found for update."
                )
                return None

            for key, value in update_data.items():
                setattr(obj, key, value)

            self.db_session.commit()
            self.db_session.refresh(obj)
            logger.debug(f"Successfully updated {model.__name__}: {obj}")
            return obj
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logger.error(
                f"Failed to update {model.__name__} with id {obj_id}: {e}"
            )
            return None

    def delete(
        self, model: Type[T], obj_id: Any, hard_delete: bool = False
    ) -> bool:
        """Delete an existing record by ID."""
        try:
            obj = self.read(model, {"id": obj_id})
            if not obj:
                logger.warning(
                    f"{model.__name__} with id {obj_id} not found for deletion."
                )
                return False

            if hard_delete:
                self.db_session.delete(obj)
            else:
                obj.is_deleted = True

            self.db_session.commit()
            logger.debug(f"Successfully deleted {model.__name__}: {obj}")
            return True
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logger.error(
                f"Failed to delete {model.__name__} with id {obj_id}: {e}"
            )
            return False

    def begin_nested(self) -> Any:
        """Support for nested transactions."""
        return self.db_session.begin_nested()
