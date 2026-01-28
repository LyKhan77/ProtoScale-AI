"""Storage modules."""
from app.storage.base import StorageBase
from app.storage.local import LocalStorage

__all__ = ["StorageBase", "LocalStorage"]
