"""Storage module for wFabricSecurity."""

from .local import LocalStorage
from .fabric_storage import FabricStorage

__all__ = ["LocalStorage", "FabricStorage"]
