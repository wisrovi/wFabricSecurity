"""Storage module for wFabricSecurity."""

from .fabric_storage import FabricStorage
from .local import LocalStorage

__all__ = ["LocalStorage", "FabricStorage"]
