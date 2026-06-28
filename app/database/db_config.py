"""
Database initialization and session management module.

This module sets up the SQLAlchemy engine and session factory for the application's SQLite database. It handles the creation of the database file and all tables defined in the model classes.
"""

from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.models import BCVRate, BinanceRate
from app.database.base import Base
from app.config import Config

#: SQLAlchemy engine instance configured for SQLite with thread-safety settings.
#: The connection uses ``check_same_thread=False`` to allow usage across multiple
#: threads, which is necessary for FastAPI's asynchronous context.
engine = create_engine(Config.DATABASE_URL, connect_args={"check_same_thread": False})

#: SQLAlchemy sessionmaker factory bound to the engine.
#: Sessions created from this factory will not auto-commit or auto-flush,
#: requiring explicit session management in the application code.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db(instance_dir: Path) -> None:
    """
    Initialize the database by creating the instance directory and all tables.

    This function ensures the specified instance directory exists, then creates all database tables defined in the SQLAlchemy metadata. If the database file does not exist, it will be created automatically by SQLAlchemy.

    Args:
        instance_dir (Path): The directory path where the SQLite database file should be stored. The function will create this directory if it doesn't already exist.

    Note:
        This function is idempotent. If the tables already exist, calling this function will have no effect (the tables will not be recreated).

    Example:
        >>> from pathlib import Path
        >>> init_db(Path("/path/to/instance"))

    Raises:
        PermissionError: If the application lacks write permissions to create the directory or database file.
        SQLAlchemyError: If there's an issue creating the database tables.
    """
    Path(instance_dir).mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)