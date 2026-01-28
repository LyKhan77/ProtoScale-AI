"""Upload service for file validation and storage."""
import os
import uuid
from pathlib import Path
from typing import BinaryIO, Tuple
from PIL import Image
import io

from app.config import get_config
from app.storage.local import get_upload_storage
from app.utils import ValidationError, get_logger

logger = get_logger(__name__)


class UploadService:
    """Service for handling file uploads."""

    def __init__(self):
        self.config = get_config()
        self.storage = get_upload_storage()

    def _get_extension(self, filename: str) -> str:
        """Get file extension from filename."""
        return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    def _is_allowed_extension(self, filename: str) -> bool:
        """Check if file extension is allowed."""
        ext = self._get_extension(filename)
        return ext in self.config.ALLOWED_EXTENSIONS

    def _validate_image(self, file_data: bytes) -> Tuple[int, int]:
        """Validate image data and return dimensions.

        Args:
            file_data: Image file bytes

        Returns:
            Tuple of (width, height)

        Raises:
            ValidationError: If image is invalid
        """
        try:
            img = Image.open(io.BytesIO(file_data))
            img.verify()
            # Re-open after verify (verify closes the file)
            img = Image.open(io.BytesIO(file_data))
            return img.size
        except Exception as e:
            raise ValidationError(f"Invalid image file: {str(e)}")

    def validate_upload(self, file: BinaryIO, filename: str) -> bytes:
        """Validate uploaded file.

        Args:
            file: File-like object
            filename: Original filename

        Returns:
            File data as bytes

        Raises:
            ValidationError: If validation fails
        """
        if not filename:
            raise ValidationError("No filename provided")

        if not self._is_allowed_extension(filename):
            raise ValidationError(
                f"Invalid file type. Allowed: {', '.join(self.config.ALLOWED_EXTENSIONS)}"
            )

        file_data = file.read()

        if len(file_data) == 0:
            raise ValidationError("Empty file")

        if len(file_data) > self.config.MAX_CONTENT_LENGTH:
            raise ValidationError(
                f"File too large. Maximum size: {self.config.MAX_CONTENT_LENGTH // (1024 * 1024)}MB"
            )

        # Validate image
        width, height = self._validate_image(file_data)
        logger.info(f"Validated image: {filename} ({width}x{height})")

        return file_data

    def save_upload(self, file_data: bytes, original_filename: str) -> str:
        """Save uploaded file to storage.

        Args:
            file_data: File data as bytes
            original_filename: Original filename for extension

        Returns:
            Relative path to saved file
        """
        ext = self._get_extension(original_filename)
        unique_filename = f"{uuid.uuid4()}.{ext}"

        self.storage.save(unique_filename, file_data)
        logger.info(f"Saved upload: {unique_filename}")

        return unique_filename

    def get_image_path(self, filename: str) -> Path:
        """Get full path to uploaded image.

        Args:
            filename: Filename in storage

        Returns:
            Full filesystem path
        """
        return self.storage.get_path(filename)


# Singleton instance
_upload_service = None


def get_upload_service() -> UploadService:
    """Get upload service singleton."""
    global _upload_service
    if _upload_service is None:
        _upload_service = UploadService()
    return _upload_service
