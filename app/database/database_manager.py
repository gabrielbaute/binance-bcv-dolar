"""
Module for managing the asynchronous database engine and sessions.
"""
import logging
from typing import AsyncGenerator
from sqlmodel import SQLModel
from sqlalchemy import event
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.config import Config, config

class DatabaseManager:
    """
    SQLite database connection manager using SQLAlchemy and SQLModel.
    Implements a singleton pattern to ensure a single instance of the engine.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        """Implement the singleton pattern.

        Returns:
            DatabaseManager: The unique instance of the DatabaseManager.
        """
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, config: Config):
        """Initialize the asynchronous engine with optimized SQLite parameters.

        Args:
            config (Config): Global application settings.
        """
        if self._initialized:
            return

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(f"Initializing engine at: {config.DATABASE_URL}")

        self.engine = create_async_engine(
            url=config.DATABASE_URL,
            echo=config.DATABASE_ECHO,
            pool_recycle=config.DATABASE_POOL_RECYCLE,
            pool_pre_ping=config.DATABASE_POOL_PRE_PING,
            connect_args={"check_same_thread": False}
        )

        event.listen(
            self.engine.sync_engine, 
            "connect", 
            self._set_sqlite_pragma
        )

        self.async_session_maker = async_sessionmaker(
            self.engine, 
            class_=AsyncSession, 
            expire_on_commit=False
        )
        self._initialized = True

    @staticmethod
    def _set_sqlite_pragma(dbapi_connection, _connection_record) -> None:
        """Configure SQLite performance PRAGMAs on connection.

        Args:
            dbapi_connection: The native DBAPI connection object.
            _connection_record: The internal SQLAlchemy connection record object.
        """
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()

    async def init_db(self) -> None:
        """Create the tables in the database if they do not exist.

        Raises:
            Exception: If the database initialization or metadata creation fails.
        """
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(SQLModel.metadata.create_all)
            self.logger.info("Database successfully initialized.")
        except Exception as e:
            self.logger.error(f"Error initializing the database: {e}")
            raise

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Provides an asynchronous session for dependency injection.

        Yields:
            AsyncSession: Active session linked to the asynchronous engine.
        """
        async with self.async_session_maker() as session:
            try:
                yield session
            finally:
                await session.close()


db_manager = DatabaseManager(config=config)