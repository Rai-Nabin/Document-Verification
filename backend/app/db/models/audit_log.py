"""
File Path: app/db/models/audit_log.py
"""

from app.db import Base
from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship


class AuditLog(Base):
    """
    Defines the SQLAlchemy model for the 'audit_logs' table in a PostgreSQL
    database, mapping Python class attributes to database columns with
    specified data types and constraints.
    """

    __tablename__ = "audit_logs"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
        comment="Unique identifier",
    )
    user_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False,
        comment="Foreign key to users table",
    )
    action = Column(
        String,
        nullable=False,
        comment='e.g., "user_login", "upload_document", "verify_document", etc.',
    )
    detail = Column(String, nullable=True, comment="Additional context")
    timestamp = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        comment="Timestamp when the audit log entry was created",
    )
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        comment="Timestamp when the audit log record was created",
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="Timestamp when the audit log record was last updated",
    )
    user = relationship("User", back_populates="audit_logs")
