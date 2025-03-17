"""
File Path: app/db/crud/user.py

User CRUD Operations for Document Verification System

This module provides Create, Read, Update, Delete (CRUD) operations for the User model.
It integrates with SQLAlchemy for database interactions, handles password hashing via
security utilities, and logs all actions for traceability. Designed to work with UserCreate
and UserUpdate schemas.

Usage:
- Instantiate with a database session: `crud = UserCRUD(db)`
- Call methods like `crud.create_user(user_data)` to manage users.
"""

from typing import Optional

from app.core import security
from app.db.models import User
from app.schemas import UserCreate, UserUpdate
from app.utils import AppLogger
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

# Module-specific logger
logger = AppLogger(logger_name=__name__).get_logger()


class UserCRUD:
    """CRUD operations for the User model."""

    def __init__(self, db: Session):
        """
        Initialize UserCRUD with a database session.

        Args:
            db (Session): SQLAlchemy database session for queries and transactions.
        """
        self.db = db

    def get_user(self, user_id: int) -> Optional[User]:
        """
        Retrieve a user by their ID.

        Args:
            user_id (int): The ID of the user to fetch.

        Returns:
            Optional[User]: The User object if found, None otherwise.
        """
        user = self.db.query(User).filter(User.user_id == user_id).first()
        logger.debug(
            f"Queried user by ID {user_id}: {'found' if user else 'not found'}"
        )
        return user

    def get_all_users(self) -> list[User]:
        """Retrieve all users from the database."""
        users = self.db.query(User).all()
        logger.debug(f"Retrieved {len(users)} users")
        return users

    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Retrieve a user by their username.

        Args:
            username (str): The username to search for.

        Returns:
            Optional[User]: The User object if found, None otherwise.
        """
        user = self.db.query(User).filter(User.username == username).first()
        logger.debug(
            f"Queried user by username '{username}': {'found' if user else 'not found'}"
        )
        return user

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Retrieve a user by their email address.

        Args:
            email (str): The email address to search for.

        Returns:
            Optional[User]: The User object if found, None otherwise.
        """
        user = self.db.query(User).filter(User.email == email).first()
        logger.debug(
            f"Queried user by email '{email}': {'found' if user else 'not found'}"
        )
        return user

    def create_user(self, user: UserCreate) -> Optional[User]:
        """
        Create a new user in the database.

        Args:
            user (UserCreate): User data including username, email, and password
              (hashed internally).

        Returns:
            Optional[User]: The created User object if successful, None on failure
              (e.g., duplicate username/email).

        Raises:
            IntegrityError: Handled internally for unique constraint violations.
        """
        try:
            db_user = User(
                username=user.username,
                email=user.email,
                hashed_password=security.hash_password(user.password),
                is_active=user.is_active,
                is_superuser=user.is_superuser,
            )
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            logger.info(f"Created user '{db_user.username}' with ID {db_user.user_id}")
            return db_user
        except IntegrityError as e:
            self.db.rollback()
            logger.error(
                f"Failed to create user '{user.username}': Duplicate username or email - {str(e)}"
            )
            return None
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected error creating user '{user.username}': {str(e)}")
            return None

    def update_user(self, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """
        Update an existing user’s details.

        Args:
            user_id (int): The ID of the user to update.
            user_update (UserUpdate): Updated user data with optional fields.

        Returns:
            Optional[User]: The updated User object if successful,
              None if user not found or update fails.
        """
        db_user = self.get_user(user_id)
        if not db_user:
            logger.warning(f"User with ID {user_id} not found for update")
            return None

        try:
            # Update only fields provided in user_update
            update_data = user_update.dict(exclude_unset=True)
            if "password" in update_data:
                update_data["hashed_password"] = security.hash_password(
                    update_data.pop("password")
                )
            for key, value in update_data.items():
                setattr(db_user, key, value)

            self.db.commit()
            self.db.refresh(db_user)
            logger.info(f"Updated user with ID {db_user.user_id}")
            return db_user
        except IntegrityError as e:
            self.db.rollback()
            logger.error(
                f"Failed to update user ID {user_id}: Duplicate username or email - {str(e)}"
            )
            return None
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected error updating user ID {user_id}: {str(e)}")
            return None

    def delete_user(self, user_id: int) -> bool:
        """
        Delete a user from the database.

        Args:
            user_id (int): The ID of the user to delete.

        Returns:
            bool: True if deletion succeeds, False if user not found or deletion fails.
        """
        db_user = self.get_user(user_id)
        if not db_user:
            logger.warning(f"User with ID {user_id} not found for deletion")
            return False

        try:
            self.db.delete(db_user)
            self.db.commit()
            logger.info(f"Deleted user with ID {user_id}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete user ID {user_id}: {str(e)}")
            return False


def get_user_crud(db: Session) -> UserCRUD:
    """
    Factory function to create a UserCRUD instance.

    Args:
        db (Session): SQLAlchemy database session.

    Returns:
        UserCRUD: An instance of UserCRUD for user operations.
    """
    return UserCRUD(db)
