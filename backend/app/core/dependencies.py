"""
File Path: app/core/dependencies.py

Dependency Injection Utilities for Document Vision System.

This module defines FastAPI dependencies for database sessions and user authentication,
integrating with SQLAlchemy, JWT, and UserCRUD.

Usage:
- Database: `@app.get("/", dependencies=[Depends(get_db)])`
- Current user: `@app.get("/me", dependencies=[Depends(get_current_user)])`
- Admin user: `@app.get("/admin", dependencies=[Depends(get_admin_user)])`
"""

from typing import Generator

from app.core import security
from app.db import db_manager
from app.db.crud import UserCRUD
from app.schemas import UserResponse
from app.utils import AppLogger
from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session

# Configure logging
logger = AppLogger(logger_name="dependencies").get_logger()

# Use APIKeyHeader for simple Bearer token input
oauth2_scheme = APIKeyHeader(
    name="Authorization", scheme_name="Bearer", description="Enter 'Bearer <token>'"
)


def get_db() -> Generator[Session, None, None]:
    """
    Provide a database session for dependency injection.

    Yields:
        Session: An SQLAlchemy database session.

    Raises:
        HTTPException: 503 if database connection fails.
    """
    logger.debug("Providing new database session")
    try:
        db = next(db_manager.get_db())
    except Exception as e:
        logger.error(f"Failed to get database session: {str(e)}")
        raise HTTPException(status_code=503, detail="Database unavailable")
    try:
        yield db
    finally:
        logger.debug("Closing database session")
        db.close()


def get_current_user(
    token: str = Security(oauth2_scheme),
    db: Session = Depends(get_db),
) -> UserResponse:
    """
    Retrieve the current authenticated user based on a JWT token.

    Args:
        token (str): JWT token from Authorization header (expected format: "Bearer <token>").
        db (Session): SQLAlchemy session (injected).

    Returns:
        UserResponse: Authenticated user’s data.

    Raises:
        HTTPException: 401 if token invalid, 404 if user not found.
    """
    logger.debug("Attempting to decode JWT token")
    if not token or not token.strip().startswith("Bearer "):
        logger.warning("Invalid Authorization header format")
        raise HTTPException(status_code=401, detail="Invalid token format")
    token = token.strip()[len("Bearer ") :].strip()
    if not token:
        logger.warning("Empty token provided")
        raise HTTPException(status_code=401, detail="Token cannot be empty")
    username = security.decode_access_token(token)
    if not username:
        logger.warning("Invalid or expired JWT token provided")
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user_crud = UserCRUD(db)
    user = user_crud.get_user_by_username(username)
    if not user:
        logger.warning(f"User '{username}' not found for token")
        raise HTTPException(status_code=404, detail="User not found")
    logger.debug(f"User '{username}' authenticated successfully")
    return UserResponse.model_validate(user)


def get_admin_user(
    current_user: UserResponse = Depends(get_current_user),
) -> UserResponse:
    """
    Ensure the current user has admin privileges.

    Args:
        current_user (UserResponse): Authenticated user from get_current_user.

    Returns:
        UserResponse: Authenticated admin use's data.

    Raises:
        HTTPException: 403 if user lacks admin privileges.
    """
    if not current_user.is_superuser:
        logger.warning(f"User {current_user.user_id} denied admin access")
        raise HTTPException(status_code=403, detail="Admin access required")
    logger.info(f"Admin user {current_user.user_id} verified")
    return current_user
