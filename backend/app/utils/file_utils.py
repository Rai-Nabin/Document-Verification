"""
File Path: app/utils/file_utils.py

File Utility Operations for Document Verification System

This module provides a utility class for file-related operations, including saving uploaded files,
deleting files, and extracting file extensions. It integrates with FastAPI's UploadFile and the
application's settings for consistent file handling.

Usage:
- Instantiate: `file_utils = FileUtils()`
- Save a file: `file_path = file_utils.save_upload_file(upload_file)`
- Delete a file: `success = file_utils.delete_file(file_path)`
- Get extension: `ext = file_utils.get_file_extension(filename)`
"""

import shutil
from pathlib import Path
from typing import Optional

from app.core import settings
from app.utils import AppLogger
from fastapi import UploadFile

# Module-specific logger
logger = AppLogger(logger_name="file_utils").get_logger()


class FileUtils:
    """Utility class for file operations like saving, deleting, and inspecting files."""

    async def save_upload_file(
        self,
        upload_file: UploadFile,
        destination_dir: str = settings.UPLOAD_FOLDER,
    ) -> Optional[str]:
        """
        Save an uploaded file to the specified directory asynchronously.

        Args:
            upload_file (UploadFile): The uploaded file object from FastAPI.
            destination_dir (str): Directory to save the file (default: settings.UPLOAD_FOLDER).

        Returns:
            Optional[str]: The full file path if successful, None if an error occurs.

        Raises:
            OSError: If directory creation or file writing fails (e.g., permissions, no space).
        """
        try:
            # Sanitize filename to prevent path traversal
            filename = Path(upload_file.filename).name  # Strips any path components
            dest_path = Path(destination_dir)
            dest_path.mkdir(parents=True, exist_ok=True)

            # Construct safe file path
            file_path = dest_path / filename
            logger.debug(f"Attempting to save file to: {file_path}")

            # Write the file asynchronously
            with file_path.open("wb") as buffer:
                shutil.copyfileobj(upload_file.file, buffer)

            logger.info(f"File saved successfully: {file_path}")
            return str(file_path)
        except OSError as e:
            logger.error(f"Error saving file '{upload_file.filename}': {str(e)}")
            return None
        except Exception as e:
            logger.error(
                f"Unexpected error saving file '{upload_file.filename}': {str(e)}"
            )
            return None
        finally:
            # Ensure async file handle cleanup
            await upload_file.close()

    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from the filesystem.

        Args:
            file_path (str): The path to the file to delete.

        Returns:
            bool: True if the file was deleted, False if it doesn’t exist or an error occurs.
        """
        file_path_obj = Path(file_path)
        try:
            if file_path_obj.exists() and file_path_obj.is_file():
                file_path_obj.unlink()
                logger.info(f"File deleted successfully: {file_path}")
                return True
            logger.warning(f"File not found or not a file: {file_path}")
            return False
        except PermissionError as e:
            logger.error(f"Permission denied deleting file '{file_path}': {str(e)}")
            return False
        except OSError as e:
            logger.error(f"Error deleting file '{file_path}': {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting file '{file_path}': {str(e)}")
            return False

    def get_file_extension(self, file_name: str) -> str:
        """
        Extract the file extension from a filename.

        Args:
            file_name (str): The filename or path to extract the extension from.

        Returns:
            str: The file extension in lowercase (e.g., '.txt', '.pdf'), or empty string if none.
        """
        try:
            extension = Path(file_name).suffix.lower()
            logger.debug(f"Extracted extension '{extension}' from '{file_name}'")
            return extension
        except Exception as e:
            logger.error(f"Error extracting extension from '{file_name}': {str(e)}")
            return ""


file_utils = FileUtils()

# Example usage:
# from fastapi import UploadFile
# from app.utils.file_utils import file_utils
#
# async def upload_file(file: UploadFile):
#     file_path = await file_utils.save_upload_file(file)
#     if file_path:
#         ext = file_utils.get_file_extension(file_path)
#         # Process file...
#         file_utils.delete_file(file_path)
