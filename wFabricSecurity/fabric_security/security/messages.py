"""Message management for wFabricSecurity."""

import uuid
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

from ..core.enums import DataType
from ..core.models import Message
from ..core.exceptions import MessageIntegrityError, SignatureError

logger = logging.getLogger("FabricSecurity.Messages")


class MessageManager:
    """Manages signed messages with integrity verification."""

    def __init__(
        self,
        gateway: "FabricGateway",
        ttl_seconds: int = 3600,
        cleanup_interval: int = 300,
    ):
        """Initialize message manager.

        Args:
            gateway: Fabric Gateway instance
            ttl_seconds: Default message TTL in seconds
            cleanup_interval: Interval for cleaning expired messages
        """
        self._gateway = gateway
        self._ttl_seconds = ttl_seconds
        self._cleanup_interval = cleanup_interval
        self._last_cleanup = datetime.now()
        self._messages_cache: Dict[str, Message] = {}

    def create_message(
        self,
        sender: str,
        recipient: str,
        content: str,
        data_type: DataType = DataType.JSON,
        ttl_seconds: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Message:
        """Create a signed message.

        Args:
            sender: Sender identity
            recipient: Recipient identity
            content: Message content
            data_type: Type of data
            ttl_seconds: Custom TTL (uses default if None)
            metadata: Additional metadata

        Returns:
            Signed Message object
        """
        content_hash = self._gateway.compute_message_hash(content)
        timestamp = datetime.now().isoformat()
        message_id = str(uuid.uuid4())

        signature = self._gateway.sign(f"{sender}:{recipient}:{content_hash}", sender)

        expires_at = None
        if ttl_seconds is None:
            ttl_seconds = self._ttl_seconds
        if ttl_seconds > 0:
            expires_at = (datetime.now() + timedelta(seconds=ttl_seconds)).isoformat()

        message = Message(
            sender=sender,
            recipient=recipient,
            content=content,
            content_hash=content_hash,
            signature=signature,
            timestamp=timestamp,
            message_id=message_id,
            data_type=data_type,
            expires_at=expires_at,
            metadata=metadata or {},
        )

        self._messages_cache[message_id] = message
        self._gateway.local_storage.save_message(
            message_id, message.to_dict(), ttl_seconds
        )

        self._maybe_cleanup()

        logger.info(f"Created message {message_id} from {sender} to {recipient}")
        return message

    def verify_message(self, message: Message) -> bool:
        """Verify message integrity and signature.

        Args:
            message: Message to verify

        Returns:
            True if message is valid

        Raises:
            MessageIntegrityError: If content was modified
            SignatureError: If signature is invalid
        """
        if message.is_expired():
            logger.warning(f"Message {message.message_id} has expired")
            return False

        current_hash = self._gateway.compute_message_hash(message.content)
        if current_hash != message.content_hash:
            raise MessageIntegrityError(
                message="Message content has been modified.",
                details={
                    "message_id": message.message_id,
                    "expected_hash": message.content_hash,
                    "actual_hash": current_hash,
                },
            )

        signature_data = f"{message.sender}:{message.recipient}:{message.content_hash}"
        is_valid = self._gateway.verify_signature(
            signature_data,
            message.signature,
            message.sender,
        )

        if not is_valid:
            raise SignatureError(
                message="Message signature is invalid.",
                details={"message_id": message.message_id, "sender": message.sender},
            )

        logger.debug(f"Message {message.message_id} verified successfully")
        return True

    def get_message(self, message_id: str) -> Optional[Message]:
        """Get a message by ID.

        Args:
            message_id: Message ID

        Returns:
            Message or None if not found
        """
        if message_id in self._messages_cache:
            return self._messages_cache[message_id]

        message_dict = self._gateway.local_storage.get_message(message_id)
        if message_dict:
            message = Message.from_dict(message_dict)
            self._messages_cache[message_id] = message
            return message

        return None

    def get_messages_for_recipient(self, recipient: str) -> List[Message]:
        """Get all messages for a recipient.

        Args:
            recipient: Recipient identity

        Returns:
            List of messages
        """
        messages = []
        for message_id in self._gateway.local_storage.list_keys("msg_"):
            message = self.get_message(message_id.replace("msg_", ""))
            if message and message.recipient == recipient and not message.is_expired():
                messages.append(message)
        return messages

    def get_messages_from_sender(self, sender: str) -> List[Message]:
        """Get all messages from a sender.

        Args:
            sender: Sender identity

        Returns:
            List of messages
        """
        messages = []
        for message_id in self._gateway.local_storage.list_keys("msg_"):
            message = self.get_message(message_id.replace("msg_", ""))
            if message and message.sender == sender and not message.is_expired():
                messages.append(message)
        return messages

    def cleanup_expired(self) -> int:
        """Clean up expired messages.

        Returns:
            Number of messages cleaned up
        """
        count = self._gateway.local_storage.cleanup_expired_messages()
        expired_cache = [
            msg_id for msg_id, msg in self._messages_cache.items() if msg.is_expired()
        ]
        for msg_id in expired_cache:
            del self._messages_cache[msg_id]
        count += len(expired_cache)
        self._last_cleanup = datetime.now()
        return count

    def _maybe_cleanup(self) -> None:
        """Clean up if enough time has passed."""
        elapsed = (datetime.now() - self._last_cleanup).total_seconds()
        if elapsed > self._cleanup_interval:
            self.cleanup_expired()

    def create_json_message(
        self,
        sender: str,
        recipient: str,
        data: dict,
        **kwargs,
    ) -> Message:
        """Create a JSON message.

        Args:
            sender: Sender identity
            recipient: Recipient identity
            data: JSON data
            **kwargs: Additional arguments for create_message

        Returns:
            Message object
        """
        content = json.dumps(data, sort_keys=True)
        return self.create_message(sender, recipient, content, DataType.JSON, **kwargs)

    def create_binary_message(
        self,
        sender: str,
        recipient: str,
        data: bytes,
        **kwargs,
    ) -> Message:
        """Create a binary data message.

        Args:
            sender: Sender identity
            recipient: Recipient identity
            data: Binary data
            **kwargs: Additional arguments for create_message

        Returns:
            Message object
        """
        import base64

        content = base64.b64encode(data).decode()
        return self.create_message(
            sender, recipient, content, DataType.BINARY, **kwargs
        )

    def parse_json_content(self, message: Message) -> dict:
        """Parse JSON content from message.

        Args:
            message: Message with JSON content

        Returns:
            Parsed JSON data
        """
        return json.loads(message.content)

    def parse_binary_content(self, message: Message) -> bytes:
        """Parse binary content from message.

        Args:
            message: Message with binary content

        Returns:
            Binary data
        """
        import base64

        return base64.b64decode(message.content)
