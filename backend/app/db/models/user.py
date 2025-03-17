"""
File Path: app/db/models/user.py
"""

from app.db import Base
from sqlalchemy import TIMESTAMP, Boolean, Column, Integer, String, func
from sqlalchemy.orm import relationship


class User(Base):
    """
    Defines the SQLAlchemy model for the 'users' table in a PostgreSQL
    database, mapping Python class attributes to database columns with
    specified data types and constraints.
    """

    __tablename__ = "users"

    user_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
        comment="Unique identifier",
    )
    username = Column(
        String(255),
        unique=True,
        nullable=False,
        comment="User's username (must be unique)",
    )
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="User's email address (must be unique)",
    )
    hashed_password = Column(
        String,
        nullable=False,
        comment="Hashed password (never store plain text passwords)",
    )
    is_active = Column(
        Boolean, default=True, comment="Indicates if the user is active"
    )  # noqa
    is_superuser = Column(
        Boolean, default=False, comment="Indicates if the user is an admin"
    )
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        comment="Timestamp when the user was created",
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="Timestamp when the user was last updated",
    )
    documents = relationship("Document", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")
