"""
File Path: app/schemas/verification.py

Verification Schemas for Document Verification System.

This module defines Pydantic models for verification-related data in the application.
These schemas handle input validation, serialization, and API responses for verification operations,
integrating with SQLAlchemy models via CRUD operations to track document verification status.

Classes:
- VerificationBase: Shared attributes for all verification schemas.
- VerificationCreate: Schema for creating new verification records.
- VerificationUpdate: Schema for updating existing verification records (optional fields).
- VerificationResponse: Schema for API responses with database-generated fields.

Usage:
- Input: `VerificationCreate` for POST requests, `VerificationUpdate` for PATCH requests.
- Output: `VerificationResponse` for returning verification data in API responses.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class VerificationBase(BaseModel):
    """
    Base schema for verification attributes shared across create, update, and response models.

    Attributes:
        document_id (int): The ID of the document being verified.
        status (str): Verification status (e.g., 'pending', 'approved', 'rejected').
        result_detail (Optional[str]): Additional details about the verification result.
        is_valid (bool): Indicates if the verification result is valid.
    """

    document_id: int = Field(gt=0, description="ID of the document being verified")
    status: str = Field(
        min_length=1,
        max_length=50,
        description="Verification status (e.g., 'pending', 'approved', 'rejected')",
    )
    result_detail: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Optional details about the verification result",
    )
    is_valid: bool = Field(description="Indicates if the verification is valid")


class VerificationCreate(VerificationBase):
    """
    Schema for creating a new verification record.

    Inherits all fields from VerificationBase with no additional attributes required.
    """


class VerificationUpdate(BaseModel):
    """
    Schema for updating an existing verification record, with all fields optional.

    Attributes:
        status (Optional[str]): Updated verification status, if provided.
        result_detail (Optional[str]): Updated verification details, if provided.
        is_valid (Optional[bool]): Updated validity status, if provided.
    """

    status: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=50,
        description="Updated verification status (e.g., 'pending', 'approved', 'rejected')",
    )
    result_detail: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Updated details about the verification result",
    )
    is_valid: Optional[bool] = Field(
        default=None, description="Updated validity status"
    )


class VerificationResponse(VerificationBase):
    """
    Schema for returning verification data in API responses, including database fields.

    Attributes:
        id (int): Unique identifier from the database.
        verified_at (Optional[datetime]): Timestamp of verification completion, if applicable.
        created_at (datetime): Timestamp of record creation.
        updated_at (datetime): Timestamp of last update.
    """

    id: int = Field(description="Unique verification record ID from database")
    verified_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when the document was verified, if completed",
    )
    created_at: datetime = Field(
        description="Timestamp of verification record creation"
    )
    updated_at: datetime = Field(description="Timestamp of last update")

    class Config:
        """Pydantic configuration to enable ORM compatibility."""

        from_attributes = True  # Maps SQLAlchemy model attributes to this schema


# Optional: Example usage for testing
if __name__ == "__main__":
    # Test VerificationCreate validation
    verification = VerificationCreate(
        document_id=1, status="approved", result_detail="Looks good", is_valid=True
    )
    print(verification.model_dump_json())
