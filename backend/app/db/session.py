"""
File Path: app/db/session.py

Database session management for the Document Verification System.

This module defines a DatabaseSessionManager class to handle SQLAlchemy engine creation,
session factory setup, and database session provisioning for FastAPI routes. It supports
lazy initialization, table creation for development, and proper resource cleanup.
"""

from app.core import settings
from app.db import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class DatabaseSessionManager:
    """
    Manages the SQLAlchemy database engine, session factory, and provides a
    dependency for FastAPI routes.
    Also provides functionality to create database tables.
    """

    def __init__(self, database_url: str, echo: bool = False):
        """
        Initializes the DatabaseSessionManager.

        Args:
            database_url (str): The database connection URL.
            echo (bool): If True, SQLAlchemy will log all SQL statements
              (default: False).
        """
        self.database_url = database_url
        self.echo = echo
        self.engine = None
        self.SessionLocal = None

    def init(self):
        """Initializes the engine and session factory lazily."""
        if not self.engine:
            self.engine = create_engine(
                self.database_url, echo=self.echo, pool_size=5, max_overflow=10
            )
        if not self.SessionLocal:
            self.SessionLocal = sessionmaker(
                autocommit=False, autoflush=False, bind=self.engine
            )

    def get_db(self):
        """
        Dependency for FastAPI routes. Yields a database session.
        Ensures the session is closed after the route handler finishes.
        """
        self.init()  # Lazy initialization
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def create_tables(self):
        """
        Creates all tables defined in the SQLAlchemy metadata.
        DO NOT use in production; use Alembic instead.
        """
        self.init()
        Base.metadata.create_all(bind=self.engine)

    def dispose(self):
        """Disposes of the engine, closing all connections."""
        if self.engine:
            self.engine.dispose()
            self.engine = None
            self.SessionLocal = None


# Instantiate the manager (no immediate engine/session creation)
db_manager = DatabaseSessionManager(settings.DATABASE_URL)
