"""
File Path: app/utils/response_utils.py

API Response Utilities for Document Verification System

This module provides functions to generate standardized API responses for success and
 error scenarios.
Responses follow a consistent format using a Pydantic model, integrating with
 FastAPI's JSONResponse
and the application's logging system.

Usage:
- Success: `return success_response(data={"id": 1}, message="Item retrieved")`
- Error: `return error_response("Invalid input", status.HTTP_400_BAD_REQUEST)`
- Specific errors: `return not_found_response("Item not found")`
"""

from typing import Any, Optional

from app.utils.logging import AppLogger
from fastapi import status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Module-specific logger
logger = AppLogger(logger_name=__name__).get_logger()


class APIResponse(BaseModel):
    """
    Standardized API response model for success and error responses.

    Attributes:
        status (str): Response status ('success' or 'error').
        message (Optional[str]): Descriptive message about the response.
        data (Optional[Any]): Response data (e.g., retrieved object).
    """

    status: str = Field(description="Response status: 'success' or 'error'")
    message: Optional[str] = Field(default=None, description="Descriptive message")
    data: Optional[Any] = Field(default=None, description="Response data")

    class Config:
        """Pydantic configuration for serialization."""

        from_attributes = True  # Enables mapping from attributes if needed


def success_response(data: Any = None, message: str = "Success") -> JSONResponse:
    """
    Generate a standardized success response (HTTP 200).

    Args:
        data (Any, optional): Data to include in the response (e.g., dict, list).
        message (str, optional): Success message (default: "Success").

    Returns:
        JSONResponse: A JSON response with status code 200.
    """
    response = APIResponse(status="success", message=message, data=data)
    logger.info(f"Success response: {message}")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=response.model_dump(exclude_none=True),
    )


def error_response(
    message: str,
    status_code: int = status.HTTP_400_BAD_REQUEST,
    data: Any = None,
    headers: Optional[dict] = None,
) -> JSONResponse:
    """
    Generate a standardized error response.

    Args:
        message (str): Error message to include in the response.
        status_code (int, optional): HTTP status code (default: 400 Bad Request).
        data (Any, optional): Additional error details (e.g., validation errors).
        headers (Optional[dict], optional): Additional headers (e.g., WWW-Authenticate).

    Returns:
        JSONResponse: A JSON response with the specified error status code.
    """
    response = APIResponse(status="error", message=message, data=data)
    log_level = logger.error if status_code >= 500 else logger.warning
    log_level(f"Error response [HTTP {status_code}]: {message}")
    return JSONResponse(
        status_code=status_code,
        content=response.model_dump(exclude_none=True),
        headers=headers,
    )


def not_found_response(message: str = "Resource not found") -> JSONResponse:
    """
    Generate a standardized 404 (Not Found) response.

    Args:
        message (str, optional): Not found message (default: "Resource not found").

    Returns:
        JSONResponse: A JSON response with status code 404.
    """
    return error_response(message, status_code=status.HTTP_404_NOT_FOUND)


def unauthorized_response(message: str = "Unauthorized") -> JSONResponse:
    """
    Generate a standardized 401 (Unauthorized) response with WWW-Authenticate header.

    Args:
        message (str, optional): Unauthorized message (default: "Unauthorized").

    Returns:
        JSONResponse: A JSON response with status code 401.
    """
    headers = {"WWW-Authenticate": "Bearer"}
    return error_response(
        message, status_code=status.HTTP_401_UNAUTHORIZED, headers=headers
    )


def forbidden_response(message: str = "Forbidden") -> JSONResponse:
    """
    Generate a standardized 403 (Forbidden) response.

    Args:
        message (str, optional): Forbidden message (default: "Forbidden").

    Returns:
        JSONResponse: A JSON response with status code 403.
    """
    return error_response(message, status_code=status.HTTP_403_FORBIDDEN)


def internal_server_error_response(
    message: str = "Internal Server Error",
) -> JSONResponse:
    """
    Generate a standardized 500 (Internal Server Error) response.

    Args:
        message (str, optional): Error message (default: "Internal Server Error").

    Returns:
        JSONResponse: A JSON response with status code 500.
    """
    return error_response(message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Example usage with FastAPI:
# from fastapi import FastAPI
# from app.utils.response_utils import success_response, not_found_response, unauthorized_response
#
# app = FastAPI()
#
# @app.get("/item/{id}")
# async def get_item(id: int):
#     if id == 1:
#         return success_response(data={"id": 1, "name": "Item"}, message="Item retrieved")
#     return not_found_response(f"Item {id} not found")
#
# @app.get("/protected")
# async def protected_route(token: str):
#     if token != "valid":
#         return unauthorized_response("Invalid token")
#     return success_response(data={"message": "Protected data"})
