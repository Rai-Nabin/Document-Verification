"""
File Path: app/db/base.py
"""

from sqlalchemy.orm import DeclarativeBase


# Define the base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass
