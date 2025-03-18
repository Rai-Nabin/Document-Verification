"""
File Path: app/db/crud/verification.py

Verification CRUD Operations for Document Verification System

This module provides Create, Read, Update, Delete (CRUD) operations for the Verification model.
It integrates with SQLAlchemy for database interactions and logs all actions for traceability.
Designed to work with VerificationCreate and VerificationUpdate schemas.

Usage:
- Instantiate with a database session: `crud = VerificationCRUD(db)`
- Call methods like `crud.create_verification(ver_data)` to manage verification records.
"""

from typing import Optional

from app.db.models import Verification
from app.schemas import VerificationCreate, VerificationUpdate
from app.utils import AppLogger
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

# Module-specific logger
logger = AppLogger(logger_name=__name__).get_logger()


class VerificationCRUD:
    """CRUD operations for the Verification model."""

    def __init__(self, db: Session):
        """
        Initialize VerificationCRUD with a database session.

        Args:
            db (Session): SQLAlchemy database session for queries and transactions.
        """
        self.db = db

    def get_verification(self, verification_id: int) -> Optional[Verification]:
        """
        Retrieve a verification record by its ID.

        Args:
            verification_id (int): The ID of the verification to fetch.

        Returns:
            Optional[Verification]: The Verification object if found, None otherwise.
        """
        ver = (
            self.db.query(Verification)
            .filter(Verification.id == verification_id)
            .first()
        )
        logger.debug(
            f"Queried verification by ID {verification_id}: {'found' if ver else 'not found'}"
        )
        return ver

    def create_verification(
        self, verification: VerificationCreate
    ) -> Optional[Verification]:
        """
        Create a new verification record in the database.

        Args:
            verification (VerificationCreate): Verification data including document_id,
              status, and is_valid.

        Returns:
            Optional[Verification]: The created Verification object if successful, None on failure.

        Raises:
            IntegrityError: Handled internally for constraint violations
              (e.g., invalid document_id).
        """
        try:
            db_verification = Verification(
                document_id=verification.document_id,
                status=verification.status,
                result_detail=verification.result_detail,
                is_valid=verification.is_valid,
            )
            self.db.add(db_verification)
            self.db.commit()
            self.db.refresh(db_verification)
            logger.info(
                f"""Created verification for document ID {db_verification.document_id}
                  with ID {db_verification.id}"""
            )
            return db_verification
        except IntegrityError as e:
            self.db.rollback()
            logger.error(
                f"""Failed to create verification for document ID {verification.document_id}:
                  Constraint violation - {str(e)}"""
            )
            return None
        except Exception as e:
            self.db.rollback()
            logger.error(
                f"""Unexpected error creating verification for document ID
                  {verification.document_id}: {str(e)}"""
            )
            return None

    def update_verification(
        self, verification_id: int, verification_update: VerificationUpdate
    ) -> Optional[Verification]:
        """
        Update an existing verification record’s details.

        Args:
            verification_id (int): The ID of the verification to update.
            verification_update (VerificationUpdate): Updated verification
              data with optional fields.

        Returns:
            Optional[Verification]: The updated Verification object if successful,
              None if not found or update fails.
        """
        db_verification = self.get_verification(verification_id)
        if not db_verification:
            logger.warning(
                f"Verification with ID {verification_id} not found for update"
            )
            return None

        try:
            # Update only fields provided in verification_update
            update_data = verification_update.dict(exclude_unset=True)
            if "is_valid" in update_data:
                update_data["verified_at"] = (
                    func.now() if update_data["is_valid"] else None
                )
            for key, value in update_data.items():
                setattr(db_verification, key, value)

            self.db.commit()
            self.db.refresh(db_verification)
            logger.info(f"Updated verification with ID {db_verification.id}")
            return db_verification
        except IntegrityError as e:
            self.db.rollback()
            logger.error(
                f"""Failed to update verification ID {verification_id}:
                  Constraint violation - {str(e)}"""
            )
            return None
        except Exception as e:
            self.db.rollback()
            logger.error(
                f"Unexpected error updating verification ID {verification_id}: {str(e)}"
            )
            return None

    def delete_verification(self, verification_id: int) -> bool:
        """
        Delete a verification record from the database.

        Args:
            verification_id (int): The ID of the verification to delete.

        Returns:
            bool: True if deletion succeeds, False if verification not found or deletion fails.
        """
        db_verification = self.get_verification(verification_id)
        if not db_verification:
            logger.warning(
                f"Verification with ID {verification_id} not found for deletion"
            )
            return False

        try:
            self.db.delete(db_verification)
            self.db.commit()
            logger.info(f"Deleted verification with ID {verification_id}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(
                f"Failed to delete verification ID {verification_id}: {str(e)}"
            )
            return False


def get_verification_crud(db: Session) -> VerificationCRUD:
    """
    Factory function to create a VerificationCRUD instance.

    Args:
        db (Session): SQLAlchemy database session.

    Returns:
        VerificationCRUD: An instance of VerificationCRUD for verification operations.
    """
    return VerificationCRUD(db)
