"""
File Path: app/db/crud/__init__.py
"""

from .document import DocumentCRUD
from .user import UserCRUD
from .verification import VerificationCRUD

__all__ = ["UserCRUD", "DocumentCRUD", "VerificationCRUD"]
