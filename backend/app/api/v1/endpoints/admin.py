"""
File Path: app/api/v1/endpoints/admin.py

Admin API Endpoints for Document Verification System

This module defines admin-only endpoints for managing users in the FastAPI application.
It integrates with UserCRUD for database operations, uses dependency injection for
database sessions and admin authentication, and returns standardized responses.

Usage:
- Get user: `GET /api/v1/admin/users/{user_id}`
- Delete user: `DELETE /api/v1/admin/users/{user_id}`
"""

from app.core.dependencies import get_admin_user, get_db
from app.db.crud.user import UserCRUD  # Adjusted import path for clarity
from app.schemas.user import UserResponse  # Adjusted import path for clarity
from app.utils.logging import AppLogger
from app.utils.response_utils import success_response
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Configure logging
logger = AppLogger(logger_name="admin_endpoints").get_logger()


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get(
    "/users/{user_id}",
    # response_model=UserResponse,  # Removed to match success_response structure
    summary="Retrieve a user by ID (Admin Only)",
)
def get_user_by_admin(
    user_id: int,
    db: Session = Depends(get_db),
    admin_user: UserResponse = Depends(get_admin_user),
) -> dict:
    """
    Retrieve a user by their ID, restricted to admin users.

    Args:
        user_id (int): The ID of the user to retrieve.
        db (Session): SQLAlchemy database session (injected).
        admin_user (UserResponse): The authenticated admin user (injected).

    Returns:
        dict: Success response with user data (e.g., {"status": "success", "data": UserResponse}).

    Raises:
        HTTPException: 404 if the user is not found.
    """
    logger.debug(f"Admin {admin_user.user_id} attempting to retrieve user {user_id}")
    user_crud = UserCRUD(db)
    user = user_crud.get_user(user_id)
    if not user:
        logger.warning(f"User {user_id} not found by admin {admin_user.user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    logger.info(f"Admin {admin_user.user_id} retrieved user {user_id}")
    return success_response(
        data=UserResponse.from_orm(user),
        message=f"User {user_id} retrieved successfully",
    )


@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a user by ID (Admin Only)",
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin_user: UserResponse = Depends(get_admin_user),
) -> dict:
    """
    Delete a user by their ID, restricted to admin users, with self-deletion protection.

    Args:
        user_id (int): The ID of the user to delete.
        db (Session): SQLAlchemy database session (injected).
        admin_user (UserResponse): The authenticated admin user (injected).

    Returns:
        dict: Success response with a message (e.g., {"status": "success", "message": ...}).

    Raises:
        HTTPException: 404 if the user is not found, 400 if attempting self-deletion.
    """
    logger.debug(f"Admin {admin_user.user_id} attempting to delete user {user_id}")
    user_crud = UserCRUD(db)
    user = user_crud.get_user(user_id)
    if not user:
        logger.warning(
            f"User {user_id} not found for deletion by admin {admin_user.user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if user.user_id == admin_user.user_id:
        logger.warning(f"Admin {admin_user.user_id} attempted self-deletion")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete self",
        )
    try:
        user_crud.delete_user(user_id)
        logger.info(f"Admin {admin_user.user_id} deleted user {user_id}")
        return success_response(message=f"User {user_id} deleted successfully")
    except Exception as e:
        logger.error(
            f"Failed to delete user {user_id} by admin {admin_user.user_id}: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user",
        )
