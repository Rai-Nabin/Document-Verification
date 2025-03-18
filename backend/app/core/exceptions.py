"""
File Path: app/core/exceptions.py

Custom Exception Handling for Document Verification System

This module defines custom exceptions and global exception handlers for the FastAPI application.
It integrates with response_utils for standardized error responses and handles validation,
authentication, and generic errors.

Usage:
- Raise exception: `raise NotFoundException("User")`
- Register handlers: `register_exception_handlers(app)` in main.py
"""

from app.utils.response_utils import error_response
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class AppException(Exception):
    """Base custom exception for application-specific errors."""

    def __init__(
        self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST
    ) -> None:
        """
        Initialize the base exception with a message and status code.

        Args:
            message (str): The error message.
            status_code (int): HTTP status code (default: 400 Bad Request).
        """
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundException(AppException):
    """Exception raised when a resource is not found."""

    def __init__(self, resource: str) -> None:
        """
        Initialize with the resource name that wasn’t found.

        Args:
            resource (str): The name of the resource (e.g., "User", "Document").
        """
        super().__init__(f"{resource} not found", status_code=status.HTTP_404_NOT_FOUND)


class UnauthorizedException(AppException):
    """Exception raised for unauthorized access attempts."""

    def __init__(self, message: str = "Unauthorized") -> None:
        """
        Initialize with an optional custom unauthorized message.

        Args:
            message (str): The error message (default: "Unauthorized").
        """
        super().__init__(message, status_code=status.HTTP_401_UNAUTHORIZED)


class ForbiddenException(AppException):
    """Exception raised for forbidden actions."""

    def __init__(self, message: str = "Forbidden") -> None:
        """
        Initialize with an optional custom forbidden message.

        Args:
            message (str): The error message (default: "Forbidden").
        """
        super().__init__(message, status_code=status.HTTP_403_FORBIDDEN)


class ValidationException(AppException):
    """Exception raised for validation errors."""

    def __init__(self, message: str = "Validation error") -> None:
        """
        Initialize with an optional custom validation error message.

        Args:
            message (str): The error message (default: "Validation error").
        """
        super().__init__(message, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register global exception handlers for the FastAPI application.

    Args:
        app (FastAPI): The FastAPI application instance.

    Handlers:
        - RequestValidationError: Handles Pydantic validation errors (422).
        - AppException: Handles custom application exceptions (e.g., 404, 401).
        - Exception: Catches unhandled exceptions (500).
    """

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """
        Handle Pydantic validation errors with detailed error information.

        Args:
            request (Request): The incoming request.
            exc (RequestValidationError): The validation error instance.

        Returns:
            JSONResponse: A 422 response with validation error details.
        """
        return error_response(
            message="Validation error",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            data={"detail": exc.errors()},
        )

    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request, exc: AppException
    ) -> JSONResponse:
        """
        Handle custom AppException subclasses with appropriate status codes.

        Args:
            request (Request): The incoming request.
            exc (AppException): The custom exception instance.

        Returns:
            JSONResponse: A response with the exception’s status code and message.
        """
        return error_response(message=exc.message, status_code=exc.status_code)

    @app.exception_handler(Exception)
    async def generic_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """
        Handle uncaught exceptions as internal server errors.

        Args:
            request (Request): The incoming request.
            exc (Exception): The unhandled exception instance.

        Returns:
            JSONResponse: A 500 response for unexpected errors.
        """
        return error_response(
            message="An unexpected error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
