"""
File Path: app/db/models/verification.py
"""

from app.db import Base
from sqlalchemy import TIMESTAMP, Boolean, Column, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship


class Verification(Base):
    """
    Defines the SQLAlchemy model for the 'verifications' table in a PostgreSQL
    database, mapping Python class attributes to database columns with
    specified data types and constraints.
    """

    __tablename__ = "verifications"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
        comment="Unique identifier",
    )
    document_id = Column(
        Integer,
        ForeignKey("documents.id"),
        nullable=False,
        unique=True,  # Added unique constraint
        comment="Foreign key to documents table",
    )
    status = Column(
        String,
        nullable=False,
        default="pending",
        comment='e.g., "pending", "approved", "rejected"',
    )
    result_detail = Column(
        String, nullable=True, comment="Optional details about verification"
    )
    verified_at = Column(
        TIMESTAMP(timezone=True),
        nullable=True,
        comment="Timestamp when the document was verified",
    )
    is_valid = Column(
        Boolean, default=False, comment="Indicates if the verification is valid"
    )
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        comment="Timestamp when the verification record was created",
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="Timestamp when the verification record was last updated",
    )
    document = relationship("Document", back_populates="verification")
