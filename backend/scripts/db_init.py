"""
File Path: scripts/db_init.py

Database Initialization Script for Document Verification.

This script initializes the database by establishing a connection, optionally
creating tables (development only), and applying Alembic migrations.
It ensures the database structure is set up correctly for the application to store
users, documents, verifications, and audit logs. Seeding of test data is handled
separately by `seed_data.py`.

Real-Life Purpose:
- Development: Quickly sets up a database with tables for testing
 (e.g., `python scripts/db_init.py --create-tables`).
- Production: Applies migrations to update the database schema on a live server
 (e.g., `python scripts/db_init.py`).
- Troubleshooting: Verifies connectivity and schema state without modifying data.

Usage:
- `python scripts/db_init.py` - Connects and applies migrations.
- `python scripts/db_init.py --no-migrate` - Connects only, skips migrations.
- `python scripts/db_init.py --create-tables` - Connects and creates tables (dev only).

Note: Table creation is restricted to development environments for safety.
"""

import argparse
import subprocess

import sqlalchemy
from app.core import settings
from app.db import db_manager

# Import models to register with Base.metadata
from app.db.models import AuditLog, Document, User, Verification  # noqa
from app.utils import AppLogger

logger = AppLogger(logger_name=__name__).get_logger()


def init_database(apply_migrations: bool = True, create_tables: bool = False) -> None:
    """Initialize the database, optionally create tables, and apply Alembic migrations."""
    try:
        logger.info(f"Initializing database with URL: {settings.DATABASE_URL}")
        db_manager.init()
        logger.info("Database connection initialized")

        # Check database connectivity
        with db_manager.engine.connect() as conn:
            conn.execute(sqlalchemy.text("SELECT 1"))
        logger.info("Database connectivity verified")

        # Optionally create tables (development only)
        if create_tables:
            logger.info("Creating database tables")
            db_manager.create_tables()
            logger.info("Database tables created")

        # Optionally apply Alembic migrations
        if apply_migrations:
            logger.info("Applying Alembic migrations")
            if not check_alembic_installed():
                logger.error(
                    "Alembic is not installed or not found in the environment."
                )
                raise EnvironmentError("Alembic is required to apply migrations.")

            result = subprocess.run(
                ["alembic", "upgrade", "head"],
                check=True,
                capture_output=True,
                text=True,
            )
            logger.info(f"Alembic output: {result.stdout}")
            if result.stderr:
                logger.warning(f"Alembic warnings/errors: {result.stderr}")
        else:
            logger.info("Skipping migrations (use --migrate to apply)")

    except subprocess.CalledProcessError as e:
        logger.error(f"Alembic migration failed: {e.stderr}")
        raise
    except EnvironmentError as e:
        logger.error(f"Environment error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise


def check_alembic_installed() -> bool:
    """Check if Alembic is installed in the current environment."""
    try:
        subprocess.run(
            ["alembic", "--version"], check=True, capture_output=True, text=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


def main():
    """Parse CLI arguments and initialize the database."""
    parser = argparse.ArgumentParser(
        description="Initialize the database for the application."
    )
    parser.add_argument(
        "--no-migrate",
        action="store_true",
        help="Skip applying Alembic migrations (only initialize connection)",
    )
    parser.add_argument(
        "--create-tables",
        action="store_true",
        help="Create database tables (development use only)",
    )

    args = parser.parse_args()

    # Safety check for production
    if settings.ENVIRONMENT != "development" and args.create_tables:
        logger.error("Table creation is only allowed in the development environment.")
        raise EnvironmentError("Table creation is not allowed in production.")

    init_database(
        apply_migrations=not args.no_migrate, create_tables=args.create_tables
    )


if __name__ == "__main__":
    main()
