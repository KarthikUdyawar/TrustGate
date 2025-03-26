"""Database configuration module.

This module sets up the database connection using SQLAlchemy.
It includes:
- Engine creation
- Session factory
- Declarative base
- Dependency injection for DB sessions
"""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from core.config import get_settings

settings = get_settings()

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
