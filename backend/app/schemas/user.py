"""
File Path: app/schemas/user.py

User Schemas for Document Verification System.

This module defines Pydantic models for user-related data in the application.
These schemas handle input validation, serialization, and API responses for
user operations, integrating with SQLAlchemy models via CRUD operations.

Classes:
- UserBase: Shared attributes for all user schemas.
- UserCreate: Schema for creating new users.
- UserUpdate: Schema for updating existing users (optional fields).
- UserResponse: Schema for API responses with database-generated fields.

Usage:
- Input: `UserCreate` for POST requests, `UserUpdate` for PATCH requests.
- Output: `UserResponse` for returning user data in API responses.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """
    Base schema for user attributes shared across create, update, and response models.

    Attributes:
        username (str): The user's unique username.
        email (EmailStr): The user's email address.
    """

    username: str = Field(
        min_length=3, max_length=50, description="Unique username (3-50 characters)"
    )
    email: EmailStr = Field(description="User's email address")


class UserCreate(UserBase):
    """
    Schema for creating a new user, including required password and optional flags.

    Attributes:
        password (str): Plain-text password to be hashed.
        is_active (bool): Whether the user account is active (default: True).
        is_superuser (bool): Whether the user has admin privileges (default: False).
    """

    password: str = Field(
        min_length=8,
        description="Plain-text password (min 8 characters, hashed in backend)",
    )
    is_active: bool = Field(default=True, description="User account active status")
    is_superuser: bool = Field(default=False, description="Superuser privilege status")


class UserUpdate(BaseModel):
    """
    Schema for updating an existing user, with all fields optional.

    Attributes:
        username (Optional[str]): New username, if provided.
        email (Optional[EmailStr]): New email address, if provided.
        password (Optional[str]): New password, if provided (hashed in backend).
        is_active (Optional[bool]): Updated active status, if provided.
        is_superuser (Optional[bool]): Updated superuser status, if provided.
    """

    username: Optional[str] = Field(
        None,
        min_length=3,
        max_length=50,
        description="Updated username (3-50 characters)",
    )
    email: Optional[EmailStr] = Field(None, description="Updated email address")
    password: Optional[str] = Field(
        None,
        min_length=8,
        description="Updated password (min 8 characters, hashed in backend)",
    )
    is_active: Optional[bool] = Field(None, description="Updated active status")
    is_superuser: Optional[bool] = Field(None, description="Updated superuser status")


class UserResponse(UserBase):
    """
    Schema for returning user data in API responses, including database fields.

    Attributes:
        user_id (int): Unique identifier from the database.
        created_at (datetime): Timestamp of user creation.
        updated_at (datetime): Timestamp of last update.
        is_active (bool): Current active status.
        is_superuser (bool): Current superuser status.
    """

    user_id: int = Field(description="Unique user ID from database")
    created_at: datetime = Field(description="Timestamp of user creation")
    updated_at: datetime = Field(description="Timestamp of last update")
    is_active: bool = Field(description="User account active status")
    is_superuser: bool = Field(description="Superuser privilege status")

    class Config:
        """Pydantic configuration to enable ORM compatibility."""

        from_attributes = True  # Allows mapping from SQLAlchemy models


# Optional: Example usage for testing
if __name__ == "__main__":
    # Test UserCreate validation
    user = UserCreate(
        username="testuser", email="test@example.com", password="password123"
    )
    print(user.model_dump_json())
