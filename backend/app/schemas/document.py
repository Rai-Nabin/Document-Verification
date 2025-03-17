"""
File Path: app/schemas/document.py

Document Schemas for Document Verification System.

This module defines Pydantic models for document-related data in the application.
These schemas handle input validation, serialization, and API responses for document operations,
integrating with SQLAlchemy models via CRUD operations in the document verification workflow.

Classes:
- DocumentBase: Shared attributes for all document schemas.
- DocumentCreate: Schema for creating new documents.
- DocumentUpdate: Schema for updating existing documents (optional fields).
- DocumentResponse: Schema for API responses with database-generated fields.

Usage:
- Input: `DocumentCreate` for POST requests, `DocumentUpdate` for PATCH requests.
- Output: `DocumentResponse` for returning document data in API responses.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class DocumentBase(BaseModel):
    """
    Base schema for document attributes shared across create, update, and response models.

    Attributes:
        title (str): The document's title.
        file_path (str): The file system path where the document is stored.
    """

    title: str = Field(
        min_length=1, max_length=255, description="Document title (1-255 characters)"
    )
    file_path: str = Field(
        min_length=1,
        max_length=1024,
        description="Path to the stored document file (1-1024 characters)",
    )


class DocumentCreate(DocumentBase):
    """
    Schema for creating a new document, including required user ID.

    Attributes:
        user_id (int): The ID of the user uploading the document.
    """

    user_id: int = Field(gt=0, description="ID of the user creating the document")


class DocumentUpdate(BaseModel):
    """
    Schema for updating an existing document, with all fields optional.

    Attributes:
        title (Optional[str]): New title, if provided.
        file_path (Optional[str]): New file path, if provided.
    """

    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Updated document title (1-255 characters)",
    )
    file_path: Optional[str] = Field(
        None,
        min_length=1,
        max_length=1024,
        description="Updated path to the document file (1-1024 characters)",
    )


class DocumentResponse(DocumentBase):
    """
    Schema for returning document data in API responses, including database fields.

    Attributes:
        id (int): Unique identifier from the database.
        user_id (int): ID of the user who uploaded the document.
        uploaded_at (datetime): Timestamp of document upload.
        created_at (datetime): Timestamp of document creation.
        updated_at (datetime): Timestamp of last update.
    """

    id: int = Field(description="Unique document ID from database")
    user_id: int = Field(description="ID of the user who uploaded the document")
    uploaded_at: datetime = Field(description="Timestamp of document upload")
    created_at: datetime = Field(description="Timestamp of document creation")
    updated_at: datetime = Field(description="Timestamp of last update")

    class Config:
        """Pydantic configuration to enable ORM compatibility."""

        from_attributes = True  # Maps SQLAlchemy model attributes to this schema


# Optional: Example usage for testing
if __name__ == "__main__":
    # Test DocumentCreate validation
    doc = DocumentCreate(title="Test Doc", file_path="/docs/test.pdf", user_id=1)
    print(doc.model_dump_json())
