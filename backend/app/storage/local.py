"""Local filesystem storage implementation."""
import os
from pathlib import Path
from typing import BinaryIO, Optional

from app.storage.base import StorageBase


class LocalStorage(StorageBase):
    """Local filesystem storage implementation."""

    def __init__(self, base_dir: Path, base_url: str = "/api"):
        """Initialize local storage.

        Args:
            base_dir: Base directory for storage
            base_url: Base URL for file access
        """
        self.base_dir = Path(base_dir)
        self.base_url = base_url
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _get_full_path(self, path: str) -> Path:
        """Get full filesystem path."""
        return self.base_dir / path

    def save(self, path: str, data: bytes) -> str:
        """Save binary data to local filesystem."""
        full_path = self._get_full_path(path)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_bytes(data)
        return str(full_path)

    def save_file(self, path: str, file: BinaryIO) -> str:
        """Save file object to local filesystem."""
        full_path = self._get_full_path(path)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, "wb") as f:
            while chunk := file.read(8192):
                f.write(chunk)
        return str(full_path)

    def load(self, path: str) -> Optional[bytes]:
        """Load binary data from local filesystem."""
        full_path = self._get_full_path(path)
        if not full_path.exists():
            return None
        return full_path.read_bytes()

    def delete(self, path: str) -> bool:
        """Delete file from local filesystem."""
        full_path = self._get_full_path(path)
        if not full_path.exists():
            return False
        full_path.unlink()
        return True

    def exists(self, path: str) -> bool:
        """Check if file exists in local filesystem."""
        return self._get_full_path(path).exists()

    def get_path(self, path: str) -> Path:
        """Get full filesystem path."""
        return self._get_full_path(path)

    def get_url(self, path: str) -> str:
        """Get URL for accessing a file via API."""
        return f"{self.base_url}/files/{path}"


# Singleton storage instances
_upload_storage = None
_job_storage = None
_export_storage = None


def get_upload_storage() -> LocalStorage:
    """Get upload storage singleton."""
    global _upload_storage
    if _upload_storage is None:
        from app.config import get_config
        config = get_config()
        _upload_storage = LocalStorage(config.UPLOAD_DIR)
    return _upload_storage


def get_job_storage() -> LocalStorage:
    """Get job storage singleton."""
    global _job_storage
    if _job_storage is None:
        from app.config import get_config
        config = get_config()
        _job_storage = LocalStorage(config.JOBS_DIR)
    return _job_storage


def get_export_storage() -> LocalStorage:
    """Get export storage singleton."""
    global _export_storage
    if _export_storage is None:
        from app.config import get_config
        config = get_config()
        _export_storage = LocalStorage(config.EXPORT_DIR)
    return _export_storage
