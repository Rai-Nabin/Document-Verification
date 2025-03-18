"""
File Path: app/db/models/document.py
"""

from app.db import Base
from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship


class Document(Base):
    """
    Defines the SQLAlchemy model for the 'documents' table in a PostgreSQL
    database, mapping Python class attributes to database columns with
    specified data types and constraints.
    """

    __tablename__ = "documents"

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
    title = Column(String, nullable=False, comment="Title of the document")
    file_path = Column(String, nullable=False, comment="Path to stored file")
    uploaded_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        comment="Timestamp when the document was uploaded",
    )
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        comment="Timestamp when the document was created",
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="Timestamp when the document was last updated",
    )
    user = relationship("User", back_populates="documents")
    verification = relationship(
        "Verification", back_populates="document", uselist=False
    )
