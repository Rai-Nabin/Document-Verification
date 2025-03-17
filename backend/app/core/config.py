"""
File Path: app/core/config.py

Application Configuration Module

This module defines the settings for the Document Verification System using Pydantic's BaseSettings.
Settings are loaded from environment variables (via a .env file) with sensible defaults where applicable.
Grouped into categories for clarity: application, database, security, file uploads, and logging.
"""


from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """
    Configuration settings for the Document Verification System.

    Attributes are loaded from environment variables with defaults provided where appropriate.
    Case-sensitive to ensure exact matches with .env keys.
    """

    # --- Application Settings ---
    APP_NAME: str = "Document Verification System"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"  # Environment: development, production, testing
    DEBUG: bool = True
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # --- Database Settings ---
    DATABASE_URL: str  # Database connection URL (required, no default for safety)

    # --- Security & Authentication Settings ---
    SECRET_KEY: str  # Secret key for JWT encoding (required, no default for security)
    ALGORITHM: str = "HS256"  # JWT signing algorithm
    ACCESS_TOKEN_EXP_MIN: int = 30  # Access token expiration time in minutes

    # --- Admin User Settings ---
    ADMIN_USERNAME: str = "admin"  # Default admin username
    ADMIN_EMAIL: str = "admin@example.com"  # Default admin email
    ADMIN_PASSWORD: str = "admin123"  # Default admin password (change in production)

    # --- File Upload Settings ---
    UPLOAD_FOLDER: str = "uploads/"  # Directory for uploaded files
    MAX_FILE_SIZE: int = 10_485_760  # Max file size in bytes (default: 10MB)

    # --- Logging Settings ---
    LOG_LEVEL: str = "INFO"  # Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_DIR: str = "logs/"  # Directory for log files

    model_config = SettingsConfigDict(
        case_sensitive=True,  # Environment variable names are case-sensitive
        env_file=".env",      # Explicitly specify .env file (optional, for clarity)
        env_file_encoding="utf-8",  # Ensure proper encoding
    )


# Instantiate settings object for use throughout the application
settings = Settings()

# Optional: Validate critical settings at startup
if not settings.DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in the environment or .env file")
if not settings.SECRET_KEY:
    raise ValueError("SECRET_KEY must be set in the environment or .env file")