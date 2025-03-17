"""
File Path: app/services/auth/auth_service.py

Authentication Service for Document Verification System

This module provides a service class for user authentication and retrieval operations.
It integrates with Security for password verification and JWT handling, and UserCRUD
for database interactions, managing login workflows and user data retrieval.

Usage:
- Authenticate: `token = auth_service.authenticate_user(db, "username", "password")`
- Get user: `user = auth_service.get_current_user(db, "jwt_token")`
"""

from app.core import Security, security
from app.db.crud import UserCRUD
from app.schemas import UserResponse
from app.utils import AppLogger
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

# Configure logging
logger = AppLogger(logger_name="auth_service").get_logger()


class AuthService:
    """
    Service class for managing authentication operations.

    Attributes:
        security (Security): Instance for password hashing and JWT operations.
    """

    def __init__(self, security_instance: Security = security) -> None:
        """
        Initialize AuthService with a Security instance.

        Args:
            security_instance (Security): Instance for password and JWT operations (default: singleton security). # noqa
        """
        self.security = security_instance
        logger.info("AuthService initialized.")

    def authenticate_user(self, db: Session, username: str, password: str) -> dict:
        """
        Authenticate a user and generate a JWT token.

        Args:
            db (Session): SQLAlchemy database session for user queries.
            username (str): The username to authenticate.
            password (str): The password to verify.

        Returns:
            dict: A dictionary containing {"access_token": str, "token_type": str}.

        Raises:
            HTTPException: 400 if credentials are missing, 401 if authentication fails.
        """
        if not username or not password:
            logger.warning("Authentication attempt with empty credentials.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username and password required",
            )

        user_crud = UserCRUD(db)
        user = user_crud.get_user_by_username(username)
        if not user or not self.security.verify_password(
            password, user.hashed_password
        ):
            logger.warning(f"Authentication failed for username: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token = self.security.create_access_token(data={"sub": user.username})
        logger.info(f"User {username} authenticated successfully.")
        return {"access_token": access_token, "token_type": "bearer"}

    def get_current_user(self, db: Session, token: str) -> UserResponse:
        """
        Retrieve the current authenticated user from a JWT token.

        Args:
            db (Session): SQLAlchemy database session for user queries.
            token (str): The JWT token to decode and validate.

        Returns:
            UserResponse: The authenticated user’s data as a Pydantic model.

        Raises:
            HTTPException: 401 if the token is invalid, 404 if the user is not found.
        """
        username = self.security.decode_access_token(token)
        if username is None:
            logger.warning("Invalid token provided.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_crud = UserCRUD(db)
        user = user_crud.get_user_by_username(username)
        if user is None:
            logger.error(f"User not found for username: {username}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        logger.debug(f"Retrieved current user: {username}")
        return UserResponse.from_orm(user)


# Singleton instance with default security
auth_service = AuthService()
