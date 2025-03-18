"""
File Path: app/db/seed_data.py

Database Seeding Script for Document Verification System

This script populates the database with initial test data for development and testing purposes.
 It creates a sample user, document, verification, and audit log entry to simulate a functional
   system. It is designed to run separately
from `db_init.py`, which handles database structure initialization.

Real-Life Purpose:
- Development: Provides a quick way to populate the database with test data for feature
 testing (e.g., login, document upload).
- Testing: Resets and reseeds the database to ensure consistent test conditions
 (e.g., with `--reset`).
- Demonstration: Prepares a demo-ready database to showcase the application’s capabilities.

Usage:
- `python app/db/seed_data.py` - Seeds the database with test data,
 skipping duplicates if they exist.
- `python app/db/seed_data.py --reset` - Drops all tables, recreates them,
 and seeds fresh data (development only).

Note: Use after `db_init.py` has initialized the database structure.
 The `--reset` option is intended for development and testing.
"""

import argparse

from app.db import db_manager
from app.db.crud import UserCRUD
from app.db.models import AuditLog, Document, Verification
from app.schemas import UserCreate
from app.utils import AppLogger
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

logger = AppLogger(logger_name=__name__).get_logger()


def seed_data(db: Session, reset: bool = False) -> None:
    """
    Seed the database with initial test data.

    Args:
        db (Session): SQLAlchemy database session.
        reset (bool): If True, drops and recreates all tables before seeding (default: False).

    Raises:
        RuntimeError: If any database operation fails, with rollback.
    """
    try:
        if reset:
            logger.info("Resetting database before seeding")
            db_manager.init()
            db_manager.engine.execute(
                "DROP TABLE IF EXISTS audit_log, verification, documents, users CASCADE"
            )
            db_manager.create_tables()
            logger.info("Database reset and tables recreated")

        user_crud = UserCRUD(db)
        logger.debug("Starting database seeding process.")

        # Seed User
        username = "testuser1"
        existing_user = user_crud.get_user_by_username(username)
        if existing_user:
            logger.info(
                f"""User '{username}' already exists with ID {existing_user.user_id},
                  skipping creation.
                  """
            )
            user = existing_user
        else:
            user_data = UserCreate(
                username=username,
                email="test1@example.com",
                password="testpassword",
                is_active=True,
                is_superuser=False,
            )
            user = user_crud.create_user(user_data)
            db.commit()
            db.refresh(user)
            logger.info(f"Created user '{username}' with ID {user.user_id}.")

        # Seed Document
        document_title = "Test Doc"
        existing_document = (
            db.query(Document)
            .filter(Document.user_id == user.user_id, Document.title == document_title)
            .first()
        )
        if existing_document:
            logger.info(
                f"""Document '{document_title}' already exists for user ID {user.user_id},
                  skipping creation."""
            )
            document = existing_document
        else:
            document = Document(
                user_id=user.user_id,
                title=document_title,
                file_path="/docs/test.pdf",
                uploaded_at=func.now(),
                created_at=func.now(),
                updated_at=func.now(),
            )
            db.add(document)
            db.commit()
            db.refresh(document)
            logger.info(f"Created document '{document_title}' with ID {document.id}.")

        # Seed Verification
        existing_verification = (
            db.query(Verification)
            .filter(Verification.document_id == document.id)
            .first()
        )
        if existing_verification:
            logger.info(
                f"Verification already exists for document ID {document.id}, skipping creation."
            )
        else:
            verification = Verification(
                document_id=document.id,
                status="approved",
                is_valid=True,
                verified_at=func.now(),
                created_at=func.now(),
                updated_at=func.now(),
            )
            db.add(verification)
            db.commit()
            logger.info(f"Created verification for document ID {document.id}.")

        # Seed Audit Log
        audit_action = "user_created"
        existing_audit = (
            db.query(AuditLog)
            .filter(AuditLog.user_id == user.user_id, AuditLog.action == audit_action)
            .first()
        )
        if existing_audit:
            logger.info(
                f"""Audit log entry for '{audit_action}' already exists for user ID {user.user_id},
                  skipping creation.
                  """
            )
        else:
            audit_log = AuditLog(
                user_id=user.user_id,
                action=audit_action,
                detail="Test user seeded",
                timestamp=func.now(),
                created_at=func.now(),
                updated_at=func.now(),
            )
            db.add(audit_log)
            db.commit()
            logger.info(f"Created audit log entry for action '{audit_action}'.")

        logger.info("Database seeded successfully.")
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to seed data: {str(e)}")
        raise RuntimeError(f"Failed to seed data: {str(e)}")


def main():
    """Parse CLI arguments and seed the database."""
    parser = argparse.ArgumentParser(description="Seed the database with test data.")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset the database before seeding (drops all tables)",
    )
    args = parser.parse_args()

    db_gen = db_manager.get_db()
    db = next(db_gen)
    try:
        seed_data(db, reset=args.reset)
    finally:
        db.close()
        logger.debug("Database session closed.")


if __name__ == "__main__":
    main()
