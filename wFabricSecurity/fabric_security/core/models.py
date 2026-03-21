"""Data models for wFabricSecurity."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any

from .enums import CommunicationDirection, ParticipantStatus, TaskStatus, DataType


@dataclass
class Message:
    """Represents a signed message in the system."""

    sender: str
    recipient: str
    content: str
    content_hash: str
    signature: str
    timestamp: str
    message_id: str = ""
    data_type: DataType = DataType.JSON
    expires_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "sender": self.sender,
            "recipient": self.recipient,
            "content": self.content,
            "content_hash": self.content_hash,
            "signature": self.signature,
            "timestamp": self.timestamp,
            "message_id": self.message_id,
            "data_type": self.data_type.value
            if isinstance(self.data_type, DataType)
            else self.data_type,
            "expires_at": self.expires_at,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """Create from dictionary."""
        data_type = data.get("data_type", "json")
        if isinstance(data_type, str):
            data_type = DataType(data_type)
        return cls(
            sender=data["sender"],
            recipient=data["recipient"],
            content=data["content"],
            content_hash=data["content_hash"],
            signature=data["signature"],
            timestamp=data["timestamp"],
            message_id=data.get("message_id", ""),
            data_type=data_type,
            expires_at=data.get("expires_at"),
            metadata=data.get("metadata", {}),
        )

    def is_expired(self) -> bool:
        """Check if message has expired."""
        if not self.expires_at:
            return False
        try:
            expires = datetime.fromisoformat(self.expires_at)
            return datetime.now() > expires
        except (ValueError, TypeError):
            return False


@dataclass
class Participant:
    """Represents a participant in the Zero Trust system."""

    identity: str
    code_hash: str
    version: str = "1.0.0"
    registered_at: str = ""
    allowed_communications: List[str] = field(default_factory=list)
    direction: CommunicationDirection = CommunicationDirection.BIDIRECTIONAL
    is_active: bool = True
    status: ParticipantStatus = ParticipantStatus.ACTIVE
    revoked_at: Optional[str] = None
    last_verified: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "identity": self.identity,
            "code_hash": self.code_hash,
            "version": self.version,
            "registered_at": self.registered_at,
            "allowed_communications": self.allowed_communications,
            "direction": self.direction.value
            if isinstance(self.direction, CommunicationDirection)
            else self.direction,
            "is_active": self.is_active,
            "status": self.status.value
            if isinstance(self.status, ParticipantStatus)
            else self.status,
            "revoked_at": self.revoked_at,
            "last_verified": self.last_verified,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Participant":
        """Create from dictionary."""
        direction = data.get("direction", "bidirectional")
        if isinstance(direction, str):
            direction = CommunicationDirection(direction)
        status = data.get("status", "active")
        if isinstance(status, str):
            status = ParticipantStatus(status)
        return cls(
            identity=data["identity"],
            code_hash=data["code_hash"],
            version=data.get("version", "1.0.0"),
            registered_at=data.get("registered_at", ""),
            allowed_communications=data.get("allowed_communications", []),
            direction=direction,
            is_active=data.get("is_active", True),
            status=status,
            revoked_at=data.get("revoked_at"),
            last_verified=data.get("last_verified"),
            metadata=data.get("metadata", {}),
        )

    def is_revoked(self) -> bool:
        """Check if participant is revoked."""
        return self.status == ParticipantStatus.REVOKED

    def can_communicate_with(self, other_identity: str) -> bool:
        """Check if this participant can communicate with another."""
        if not self.is_active or self.is_revoked():
            return False
        if self.direction == CommunicationDirection.BIDIRECTIONAL:
            return True
        if self.direction == CommunicationDirection.OUTBOUND:
            return other_identity in self.allowed_communications
        return True


@dataclass
class Task:
    """Represents a task in the system."""

    task_id: str
    hash_a: str
    hash_b: Optional[str] = None
    master_id: str = ""
    slave_id: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    created_at: str = ""
    completed_at: Optional[str] = None
    master_signature: Optional[str] = None
    slave_signature: Optional[str] = None
    payload_hash: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "task_id": self.task_id,
            "hash_a": self.hash_a,
            "hash_b": self.hash_b,
            "master_id": self.master_id,
            "slave_id": self.slave_id,
            "status": self.status.value
            if isinstance(self.status, TaskStatus)
            else self.status,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "master_signature": self.master_signature,
            "slave_signature": self.slave_signature,
            "payload_hash": self.payload_hash,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """Create from dictionary."""
        status = data.get("status", "pending")
        if isinstance(status, str):
            status = TaskStatus(status)
        return cls(
            task_id=data["task_id"],
            hash_a=data["hash_a"],
            hash_b=data.get("hash_b"),
            master_id=data.get("master_id", ""),
            slave_id=data.get("slave_id"),
            status=status,
            created_at=data.get("created_at", ""),
            completed_at=data.get("completed_at"),
            master_signature=data.get("master_signature"),
            slave_signature=data.get("slave_signature"),
            payload_hash=data.get("payload_hash"),
            metadata=data.get("metadata", {}),
        )

    def is_complete(self) -> bool:
        """Check if task is completed."""
        return self.status == TaskStatus.COMPLETED and self.hash_b is not None
