"""Local file storage for wFabricSecurity."""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, List, Optional

logger = logging.getLogger("FabricSecurity.Storage")


class LocalStorage:
    """Fallback local storage when Fabric is unavailable."""

    def __init__(self, data_dir: Optional[str] = None):
        """Initialize local storage.

        Args:
            data_dir: Directory for storing data. Defaults to /tmp/fabric_security_data
        """
        if data_dir is None:
            data_dir = "/tmp/fabric_security_data"
        self._data_dir = Path(data_dir)
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._messages: List[dict] = []
        self._revoked_participants: set = set()
        logger.info(f"LocalStorage initialized at {self._data_dir}")

    def _get_filepath(self, key: str) -> Path:
        """Get filepath for a key."""
        safe_key = key.replace("/", "_").replace("\\", "_")
        return self._data_dir / f"{safe_key}.json"

    def save(self, key: str, value: Any) -> None:
        """Save data to local storage.

        Args:
            key: Storage key
            value: Data to store (must be JSON serializable)
        """
        filepath = self._get_filepath(key)
        with open(filepath, "w") as f:
            json.dump(value, f, indent=2, default=str)
        logger.debug(f"Saved to local storage: {key}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get data from local storage.

        Args:
            key: Storage key
            default: Default value if key not found

        Returns:
            Stored data or default
        """
        filepath = self._get_filepath(key)
        if filepath.exists():
            with open(filepath) as f:
                return json.load(f)
        return default

    def delete(self, key: str) -> bool:
        """Delete data from local storage.

        Args:
            key: Storage key

        Returns:
            True if deleted, False if not found
        """
        filepath = self._get_filepath(key)
        if filepath.exists():
            filepath.unlink()
            logger.debug(f"Deleted from local storage: {key}")
            return True
        return False

    def exists(self, key: str) -> bool:
        """Check if key exists in local storage.

        Args:
            key: Storage key

        Returns:
            True if exists
        """
        return self._get_filepath(key).exists()

    def list_keys(self, prefix: str = "") -> List[str]:
        """List all keys with optional prefix filter.

        Args:
            prefix: Optional prefix to filter keys

        Returns:
            List of keys
        """
        keys = []
        for filepath in self._data_dir.glob("*.json"):
            key = filepath.stem
            if not prefix or key.startswith(prefix):
                keys.append(key)
        return sorted(keys)

    def save_message(
        self, message_id: str, message: dict, ttl_seconds: int = 3600
    ) -> None:
        """Save a message with expiration.

        Args:
            message_id: Message ID
            message: Message data
            ttl_seconds: Time to live in seconds
        """
        expires_at = datetime.now() + timedelta(seconds=ttl_seconds)
        message["message_id"] = message_id
        message["expires_at"] = expires_at.isoformat()
        self._messages.append(message)
        self.save(f"msg_{message_id}", message)
        logger.debug(f"Saved message: {message_id}")

    def get_message(self, message_id: str) -> Optional[dict]:
        """Get a message if not expired.

        Args:
            message_id: Message ID

        Returns:
            Message data or None if not found/expired
        """
        message = self.get(f"msg_{message_id}")
        if message:
            expires_at = message.get("expires_at")
            if expires_at:
                try:
                    exp_time = datetime.fromisoformat(expires_at)
                    if datetime.now() > exp_time:
                        self.delete(f"msg_{message_id}")
                        return None
                except (ValueError, TypeError):
                    pass
        return message

    def get_expired_messages(self) -> List[str]:
        """Get list of expired message IDs.

        Returns:
            List of expired message IDs
        """
        expired = []
        now = datetime.now()
        for message in self._messages[:]:
            expires_at = message.get("expires_at")
            if expires_at:
                try:
                    exp_time = datetime.fromisoformat(expires_at)
                    if now > exp_time:
                        expired.append(message.get("message_id"))
                except (ValueError, TypeError):
                    pass
        return expired

    def cleanup_expired_messages(self) -> int:
        """Remove expired messages.

        Returns:
            Number of messages cleaned up
        """
        expired = self.get_expired_messages()
        count = 0
        for msg_id in expired:
            if self.delete(f"msg_{msg_id}"):
                count += 1
                for msg in self._messages[:]:
                    if msg.get("message_id") == msg_id:
                        self._messages.remove(msg)
        if count > 0:
            logger.info(f"Cleaned up {count} expired messages")
        return count

    def add_revoked_participant(self, participant_id: str) -> None:
        """Add a participant to the revocation list.

        Args:
            participant_id: Participant identity
        """
        self._revoked_participants.add(participant_id)
        self.save(
            f"revoked_{participant_id}",
            {
                "participant_id": participant_id,
                "revoked_at": datetime.now().isoformat(),
            },
        )
        logger.info(f"Revoked participant: {participant_id}")

    def is_participant_revoked(self, participant_id: str) -> bool:
        """Check if a participant is revoked.

        Args:
            participant_id: Participant identity

        Returns:
            True if revoked
        """
        if participant_id in self._revoked_participants:
            return True
        return self.exists(f"revoked_{participant_id}")

    def get_revoked_participants(self) -> List[str]:
        """Get list of all revoked participants.

        Returns:
            List of revoked participant IDs
        """
        revoked = set(self._revoked_participants)
        for key in self.list_keys("revoked_"):
            participant_id = key.replace("revoked_", "")
            revoked.add(participant_id)
        return sorted(revoked)

    def clear(self) -> None:
        """Clear all local storage."""
        for filepath in self._data_dir.glob("*.json"):
            filepath.unlink()
        self._messages.clear()
        self._revoked_participants.clear()
        logger.info("Cleared local storage")

    def get_storage_size(self) -> int:
        """Get total size of storage in bytes.

        Returns:
            Total size in bytes
        """
        total = 0
        for filepath in self._data_dir.glob("*.json"):
            total += filepath.stat().st_size
        return total

    def get_stats(self) -> dict:
        """Get storage statistics.

        Returns:
            Dictionary with storage stats
        """
        keys = self.list_keys()
        return {
            "total_keys": len(keys),
            "messages": len(self._messages),
            "revoked": len(self._revoked_participants),
            "size_bytes": self.get_storage_size(),
            "data_dir": str(self._data_dir),
        }
