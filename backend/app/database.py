"""Database session and engine setup."""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base

DB_URL = os.getenv("DB_URL", "sqlite:///./app.db")
# SQLite needs check_same_thread=False for FastAPI
connect_args = {} if not DB_URL.startswith("sqlite") else {"check_same_thread": False}
engine = create_engine(DB_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Create all tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency for FastAPI: yield a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
