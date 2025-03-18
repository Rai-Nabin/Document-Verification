"""
File Path: app/core/security.py

Security Utilities for Document Vision System.

This module provides cryptographic utilities for password hashing and JWT operations.

Usage:
- Hash password: `hashed = security.hash_password("mypassword")`
- Verify password: `is_valid = security.verify_password("mypassword", hashed)`
- Create token: `token = security.create_access_token({"sub": "user"})`
- Decode token: `username = security.decode_access_token(token)`
"""

from datetime import timedelta
from typing import Callable, Optional, Union

import jwt
from app.services.auth.jwt_handlers import JWTHandler
from app.utils import AppLogger
from fastapi import HTTPException, status
from passlib.context import CryptContext

# Configure logging
logger = AppLogger(logger_name="security").get_logger()

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Security:
    """
    Utility class for password hashing and JWT operations.

    Attributes:
        _get_password_hash (Callable[[str], str]): Function to hash passwords.
        _verify_password (Callable[[str, str], bool]): Function to verify passwords.
        jwt_handler (JWTHandler): Instance for JWT operations.
    """

    def __init__(
        self,
        get_password_hash: Callable[[str], str] = pwd_context.hash,
        verify_password: Callable[[str, str], bool] = pwd_context.verify,
    ) -> None:
        """
        Initialize Security with optional password hashing and verification functions.

        Args:
            get_password_hash (Callable[[str], str]): Function to hash a password
              (default: pwd_context.hash).
            verify_password (Callable[[str, str], bool]): Function to verify a password
              (default: pwd_context.verify).
        """
        self._get_password_hash = get_password_hash
        self._verify_password = verify_password
        self.jwt_handler = JWTHandler()
        logger.info("Security instance initialized.")

    def hash_password(self, password: str) -> str:
        """
        Hash a plaintext password using the configured hashing function.

        Args:
            password (str): The plaintext password to hash.

        Returns:
            str: The hashed password.

        Raises:
            ValueError: If the password is empty or not a string.
            Exception: Propagated from the hashing function if it fails.
        """
        if not password or not isinstance(password, str):
            logger.error("Attempted to hash invalid password.")
            raise ValueError("Password must be a non-empty string")
        try:
            return self._get_password_hash(password)
        except ValueError as ve:
            logger.error(f"Password hashing failed due to value error: {str(ve)}")
            raise
        except Exception as e:
            logger.error(f"Failed to hash password: {str(e)}")
            raise

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plaintext password against a hashed password.

        Args:
            plain_password (str): The plaintext password to verify.
            hashed_password (str): The hashed password to compare against.

        Returns:
            bool: True if the password matches, False otherwise.
        """
        if not plain_password or not hashed_password:
            logger.warning("Empty password or hash provided for verification.")
            return False
        try:
            return self._verify_password(plain_password, hashed_password)
        except ValueError as ve:
            logger.error(f"Password verification failed due to value error: {str(ve)}")
            return False
        except Exception as e:
            logger.error(f"Password verification failed: {str(e)}")
            return False

    def create_access_token(
        self,
        data: dict,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """
        Generate a JWT access token with the provided payload.

        Args:
            data (dict): Payload data to encode (e.g., {"sub": "username"}).
            expires_delta (Optional[timedelta]): Custom expiration time (default: None).

        Returns:
            str: The encoded JWT token.

        Raises:
            HTTPException: If token creation fails (status 400 or 500).
        """
        if "sub" not in data:
            logger.error("Payload missing 'sub' claim")
            raise HTTPException(status_code=400, detail="Payload must include 'sub'")
        try:
            token = self.jwt_handler.create_access_token(data, expires_delta)
            logger.debug("Access token created successfully.")
            return token
        except Exception as e:
            logger.error(f"Failed to create access token: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Token creation failed",
            )

    def decode_access_token(self, token: str) -> Union[str, None]:
        """
        Decode and validate a JWT token, extracting the username.

        Args:
            token (str): The JWT token to decode.

        Returns:
            Union[str, None]: Username from "sub" claim if valid, None if invalid or expired.
        """
        try:
            username = self.jwt_handler.decode_access_token(token)
            if username:
                logger.debug(f"Token decoded successfully for user: {username}")
            else:
                logger.warning("Token decoded but no valid username found.")
            return username
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as ite:
            logger.error(f"Invalid token: {str(ite)}")
            return None
        except Exception as e:
            logger.error(f"Failed to decode token: {str(e)}")
            return None


# Singleton instance for application-wide use
security = Security()
