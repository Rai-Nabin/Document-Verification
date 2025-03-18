"""
File Path: app/api/v1/endpoints/auth.py

Authentication API Endpoints for Document Verification System

This module defines endpoints for user registration and login, integrating with
AuthService for authentication and UserCRUD for database operations.

Usage:
- Register: `POST /api/v1/auth/register` with UserCreate payload
- Login: `POST /api/v1/auth/login` with UserCreate payload
"""

from app.core.dependencies import get_db
from app.db.crud.user import UserCRUD  # Adjusted import path
from app.schemas.user import UserCreate, UserResponse  # Adjusted import path
from app.services.auth.auth_service import auth_service  # Import the instance directly
from app.utils.logging import AppLogger
from app.utils.response_utils import error_response, success_response
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Configure logging
logger = AppLogger(logger_name="auth_endpoints").get_logger()


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    summary="Register a new user",
)
def register_user(user: UserCreate, db: Session = Depends(get_db)) -> dict:
    """
    Register a new user with a unique username.

    Args:
        user (UserCreate): The user data to register (username, email, password).
        db (Session): SQLAlchemy database session (injected).

    Returns:
        dict: Success response with the created user’s data.

    Raises:
        HTTPException: 400 if the username is already taken.
    """
    logger.debug(f"Register attempt for username: {user.username}")
    user_crud = UserCRUD(db)
    if user_crud.get_user_by_username(user.username):
        logger.warning(f"Username '{user.username}' already taken")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )
    db_user = user_crud.create_user(user)
    if not db_user:
        logger.error(f"Failed to register user '{user.username}'")
        return error_response(
            "Failed to register user", status_code=status.HTTP_400_BAD_REQUEST
        )
    logger.info(
        f"User '{user.username}' registered successfully with ID {db_user.user_id}"
    )
    return success_response(
        data=UserResponse.from_orm(db_user), message="User registered successfully"
    )


@router.post(
    "/login",
    summary="Authenticate a user and return a JWT token",
)
def login_user(user: UserCreate, db: Session = Depends(get_db)) -> dict:
    """
    Authenticate a user and return a JWT token.

    Args:
        user (UserCreate): The user credentials (username, password).
        db (Session): SQLAlchemy database session (injected).

    Returns:
        dict: Success response with {"access_token": str, "token_type": "bearer"}.

    Raises:
        HTTPException: 401 if authentication fails (via auth_service).
    """
    logger.debug(f"Login attempt for username: {user.username}")
    try:
        token_response = auth_service.authenticate_user(
            db, user.username, user.password
        )
        logger.info(f"User '{user.username}' logged in successfully")
        return success_response(data=token_response, message="Login successful")
    except HTTPException as e:
        logger.warning(f"Login failed for username '{user.username}': {e.detail}")
        raise e  # Properly re-raise the exception
