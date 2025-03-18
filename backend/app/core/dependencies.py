"""
File Path: app/core/dependencies.py

Dependency Injection Utilities for Document Verification System

This module defines FastAPI dependencies for database sessions and user authentication.
It integrates with SQLAlchemy for database access, JWT for token validation,
and user CRUD operations for retrieving authenticated users.

Usage:
- Database: `@app.get("/", dependencies=[Depends(get_db)])`
- Current user: `@app.get("/me", response_model=UserResponse, dependencies=[Depends(get_current_user)])` # noqa
- Admin user: `@app.get("/admin", dependencies=[Depends(get_admin_user)])`
"""

from typing import Generator

from app.core import security, settings
from app.db import db_manager
from app.db.crud import UserCRUD
from app.schemas import UserResponse
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

# OAuth2 scheme for JWT token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login")


def get_db() -> Generator[Session, None, None]:
    """
    Provide a database session for dependency injection.

    Yields:
        Session: An SQLAlchemy database session.

    Usage:
        `@app.get("/", dependencies=[Depends(get_db)])`
    """
    db = next(db_manager.get_db())
    yield db


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> UserResponse:
    """
    Retrieve the current authenticated user based on a JWT token.

    Args:
        token (str): The JWT token from the Authorization header (via oauth2_scheme).
        db (Session): The database session for querying the user.

    Returns:
        UserResponse: The authenticated user’s data in the UserResponse schema.

    Raises:
        HTTPException: 401 if the token is invalid, 404 if the user is not found.
    """
    username = security.decode_access_token(token)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = UserCRUD(db).get_user_by_username(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return UserResponse.from_orm(user)


def get_admin_user(
    current_user: UserResponse = Depends(get_current_user),
) -> UserResponse:
    """
    Ensure the current user has admin privileges.

    Args:
        current_user (UserResponse): The authenticated user from get_current_user.

    Returns:
        UserResponse: The authenticated admin user’s data.

    Raises:
        HTTPException: 403 if the user lacks admin privileges.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user
