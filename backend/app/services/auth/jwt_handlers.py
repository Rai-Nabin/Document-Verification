"""
File Path: app/services/auth/jwt_handler.py

JWT Token Handling for Document Verification System.

This module provides a utility class for creating and decoding JSON Web Tokens (JWT)
used in authentication workflows. It integrates with application settings for
secure token management.

Usage:
- Create token: `token = JWTHandler().create_access_token({"sub": "username"})`
- Decode token: `username = JWTHandler().decode_access_token(token)`
"""

from datetime import datetime, timedelta
from typing import Optional, Union

import jwt
from app.core import settings
from app.utils import AppLogger
from jwt.exceptions import InvalidTokenError

# Configure logging
logger = AppLogger(logger_name="jwt_handler").get_logger()


class JWTHandler:
    """
    Manages creation and decoding of JWT tokens for authentication.

    Attributes:
        SECRET_KEY (str): Secret key for signing tokens.
        ALGORITHM (str): Algorithm for token encoding/decoding (e.g., "HS256").
        ACCESS_TOKEN_EXPIRE_MINUTES (int): Default token expiration time in minutes.
    """

    def __init__(self) -> None:
        """
        Initialize JWTHandler with configuration from settings.

        Raises:
            ValueError: If SECRET_KEY, ALGORITHM, or ACCESS_TOKEN_EXP_MIN is missing.
        """
        self.SECRET_KEY = settings.SECRET_KEY
        self.ALGORITHM = settings.ALGORITHM
        self.ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXP_MIN
        if not all([self.SECRET_KEY, self.ALGORITHM, self.ACCESS_TOKEN_EXPIRE_MINUTES]):
            logger.error("JWT configuration settings are incomplete.")
            raise ValueError(
                "SECRET_KEY, ALGORITHM, and ACCESS_TOKEN_EXP_MIN must be set in settings"
            )
        logger.info("JWTHandler initialized.")

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
            Exception: If token encoding fails (e.g., invalid key or algorithm).
        """
        to_encode = data.copy()
        expire = datetime.now() + (
            expires_delta or timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        to_encode.update({"exp": expire})
        try:
            encoded_jwt = jwt.encode(
                to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM
            )
            return encoded_jwt
        except Exception as e:
            logger.error(f"JWT encoding failed: {str(e)}")
            raise

    def decode_access_token(self, token: str) -> Union[str, None]:
        """
        Decode and validate a JWT token, extracting the username.

        Args:
            token (str): The JWT token to decode.

        Returns:
            Union[str, None]: Username from "sub" claim if valid, None if invalid or missing.
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            username: str = payload.get("sub")
            if not username:
                logger.warning("JWT token has no 'sub' claim.")
            return username
        except InvalidTokenError as e:
            logger.warning(f"JWT decoding failed: {str(e)}")
            return None
