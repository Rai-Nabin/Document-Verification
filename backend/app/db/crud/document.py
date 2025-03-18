"""
File Path: app/db/crud/document.py

Document CRUD Operations for Document Verification System

This module provides Create, Read, Update, Delete (CRUD) operations for the Document model.
It integrates with SQLAlchemy for database interactions and logs all actions for traceability.
Designed to work with DocumentCreate and DocumentUpdate schemas.

Usage:
- Instantiate with a database session: `crud = DocumentCRUD(db)`
- Call methods like `crud.create_document(doc_data)` to manage documents.
"""

from typing import Optional

from app.db.models import Document
from app.schemas import DocumentCreate, DocumentUpdate
from app.utils import AppLogger
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

# Module-specific logger
logger = AppLogger(logger_name=__name__).get_logger()


class DocumentCRUD:
    """CRUD operations for the Document model."""

    def __init__(self, db: Session):
        """
        Initialize DocumentCRUD with a database session.

        Args:
            db (Session): SQLAlchemy database session for queries and transactions.
        """
        self.db = db

    def get_document(self, document_id: int) -> Optional[Document]:
        """
        Retrieve a document by its ID.

        Args:
            document_id (int): The ID of the document to fetch.

        Returns:
            Optional[Document]: The Document object if found, None otherwise.
        """
        doc = self.db.query(Document).filter(Document.id == document_id).first()
        logger.debug(
            f"Queried document by ID {document_id}: {'found' if doc else 'not found'}"
        )
        return doc

    def create_document(self, document: DocumentCreate) -> Optional[Document]:
        """
        Create a new document in the database.

        Args:
            document (DocumentCreate): Document data including user_id, title, and file_path.

        Returns:
            Optional[Document]: The created Document object if successful, None on failure.

        Raises:
            IntegrityError: Handled internally for constraint violations (e.g., foreign key errors).
        """
        try:
            db_document = Document(
                user_id=document.user_id,
                title=document.title,
                file_path=document.file_path,
            )
            self.db.add(db_document)
            self.db.commit()
            self.db.refresh(db_document)
            logger.info(
                f"Created document '{db_document.title}' with ID {db_document.id}"
            )
            return db_document
        except IntegrityError as e:
            self.db.rollback()
            logger.error(
                f"Failed to create document '{document.title}': Constraint violation - {str(e)}"
            )
            return None
        except Exception as e:
            self.db.rollback()
            logger.error(
                f"Unexpected error creating document '{document.title}': {str(e)}"
            )
            return None

    def update_document(
        self, document_id: int, document_update: DocumentUpdate
    ) -> Optional[Document]:
        """
        Update an existing document’s details.

        Args:
            document_id (int): The ID of the document to update.
            document_update (DocumentUpdate): Updated document data with optional fields.

        Returns:
            Optional[Document]: The updated Document object if successful,
              None if not found or update fails.
        """
        db_document = self.get_document(document_id)
        if not db_document:
            logger.warning(f"Document with ID {document_id} not found for update")
            return None

        try:
            # Update only fields provided in document_update
            update_data = document_update.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_document, key, value)

            self.db.commit()
            self.db.refresh(db_document)
            logger.info(f"Updated document with ID {db_document.id}")
            return db_document
        except IntegrityError as e:
            self.db.rollback()
            logger.error(
                f"Failed to update document ID {document_id}: Constraint violation - {str(e)}"
            )
            return None
        except Exception as e:
            self.db.rollback()
            logger.error(
                f"Unexpected error updating document ID {document_id}: {str(e)}"
            )
            return None

    def delete_document(self, document_id: int) -> bool:
        """
        Delete a document from the database.

        Args:
            document_id (int): The ID of the document to delete.

        Returns:
            bool: True if deletion succeeds, False if document not found or deletion fails.
        """
        db_document = self.get_document(document_id)
        if not db_document:
            logger.warning(f"Document with ID {document_id} not found for deletion")
            return False

        try:
            self.db.delete(db_document)
            self.db.commit()
            logger.info(f"Deleted document with ID {document_id}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete document ID {document_id}: {str(e)}")
            return False


def get_document_crud(db: Session) -> DocumentCRUD:
    """
    Factory function to create a DocumentCRUD instance.

    Args:
        db (Session): SQLAlchemy database session.

    Returns:
        DocumentCRUD: An instance of DocumentCRUD for document operations.
    """
    return DocumentCRUD(db)
