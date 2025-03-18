"""
File Path: scripts/create_admin.py

Admin User Creation Script for Document Verification.

This script creates an admin user in the database with superuser privileges, using settings
from `config.py` as defaults.
It checks for an existing user by username to avoid duplicates and logs the process for
traceability.

Real-Life Purpose:
- Initialization: Sets up an admin account for managing the system (e.g., approving documents).
- Automation: Can be run during deployment or manually to ensure an admin exists.
- Testing: Provides a consistent admin user for development or demo purposes.

Usage:
- `python scripts/create_admin.py` - Creates admin with defaults from settings.
- `python scripts/create_admin.py --username admin2 --email admin2@example.com --password newpass`.

Note: Ensure the database is initialized (e.g., via `db_init.py`) before running.
"""

import argparse
from typing import Optional

from app.core import security, settings
from app.db import db_manager
from app.db.crud import UserCRUD
from app.schemas import UserCreate
from app.utils import AppLogger
from sqlalchemy.orm import Session

# Initialize logger
logger = AppLogger(logger_name=__name__).get_logger()


def create_admin_user(
    db: Session,
    username: str = settings.ADMIN_USERNAME,
    email: str = settings.ADMIN_EMAIL,
    password: str = settings.ADMIN_PASSWORD,
) -> Optional[int]:
    """
    Create an admin user if it doesn’t already exist.

    Args:
        db (Session): SQLAlchemy database session.
        username (str): Username for the admin user.
        email (str): Email address for the admin user.
        password (str): Plain-text password to be hashed.

    Returns:
        Optional[int]: The created user’s ID if successful, None if user exists.

    Raises:
        ValueError: If username, email, or password is empty.
    """
    # Validate inputs
    if not all([username, email, password]):
        logger.error("Username, email, and password must not be empty.")
        raise ValueError("Username, email, and password are required.")

    user_crud = UserCRUD(db)

    # Check for existing user
    existing_user = user_crud.get_user_by_username(username)
    if existing_user:
        logger.info(
            f"Admin user '{username}' already exists with ID {existing_user.user_id}."
        )
        return None

    # Hash the password
    hashed_password = security.hash_password(password)

    # Prepare admin user data
    admin_user = UserCreate(
        username=username,
        email=email,
        password=hashed_password,
        is_active=True,
        is_superuser=True,
    )

    # Create the user
    created_user = user_crud.create_user(admin_user)
    logger.info(
        f"Admin user '{created_user.username}' created with ID {created_user.user_id}."
    )
    return created_user.user_id


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments for admin user creation.

    Returns:
        argparse.Namespace: Parsed arguments with username, email, and password.
    """
    parser = argparse.ArgumentParser(
        description="Create an admin user in the database."
    )
    parser.add_argument(
        "--username",
        default=settings.ADMIN_USERNAME,
        help=f"Admin username (default: {settings.ADMIN_USERNAME})",
    )
    parser.add_argument(
        "--email",
        default=settings.ADMIN_EMAIL,
        help=f"Admin email (default: {settings.ADMIN_EMAIL})",
    )
    parser.add_argument(
        "--password",
        default=settings.ADMIN_PASSWORD,
        help=f"Admin password (default: {settings.ADMIN_PASSWORD})",
    )
    return parser.parse_args()


def main() -> None:
    """Main function to initialize the database connection and create an admin user."""
    # Parse CLI arguments
    args = parse_args()

    # Initialize database session
    db_manager.init()
    db = next(db_manager.get_db())

    try:
        # Create admin user and commit if successful
        user_id = create_admin_user(db, args.username, args.email, args.password)
        if user_id is not None:
            db.commit()
    except Exception as e:
        logger.error(f"Failed to create admin user: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()
        logger.debug("Database session closed.")


if __name__ == "__main__":
    main()
