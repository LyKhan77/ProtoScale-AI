"""Abstract storage interface."""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import BinaryIO, Optional


class StorageBase(ABC):
    """Abstract base class for storage implementations."""

    @abstractmethod
    def save(self, path: str, data: bytes) -> str:
        """Save binary data to storage.

        Args:
            path: Relative path within storage
            data: Binary data to save

        Returns:
            Full path or URL to saved file
        """
        pass

    @abstractmethod
    def save_file(self, path: str, file: BinaryIO) -> str:
        """Save file object to storage.

        Args:
            path: Relative path within storage
            file: File-like object to save

        Returns:
            Full path or URL to saved file
        """
        pass

    @abstractmethod
    def load(self, path: str) -> Optional[bytes]:
        """Load binary data from storage.

        Args:
            path: Relative path within storage

        Returns:
            Binary data or None if not found
        """
        pass

    @abstractmethod
    def delete(self, path: str) -> bool:
        """Delete file from storage.

        Args:
            path: Relative path within storage

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    def exists(self, path: str) -> bool:
        """Check if file exists in storage.

        Args:
            path: Relative path within storage

        Returns:
            True if exists, False otherwise
        """
        pass

    @abstractmethod
    def get_path(self, path: str) -> Path:
        """Get full filesystem path for a relative path.

        Args:
            path: Relative path within storage

        Returns:
            Full filesystem path
        """
        pass

    @abstractmethod
    def get_url(self, path: str) -> str:
        """Get URL for accessing a file.

        Args:
            path: Relative path within storage

        Returns:
            URL string for accessing the file
        """
        pass
