"""Enums for wFabricSecurity."""

from enum import Enum


class CommunicationDirection(str, Enum):
    """Direction of communication between participants."""

    OUTBOUND = "outbound"
    INBOUND = "inbound"
    BIDIRECTIONAL = "bidirectional"

    def __str__(self) -> str:
        return self.value


class ParticipantStatus(str, Enum):
    """Status of a participant in the system."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    REVOKED = "revoked"
    SUSPENDED = "suspended"

    def __str__(self) -> str:
        return self.value


class DataType(str, Enum):
    """Supported data types for messages."""

    JSON = "json"
    IMAGE = "image"
    P2P = "p2p"
    BINARY = "binary"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def from_extension(cls, ext: str) -> "DataType":
        """Infer data type from file extension."""
        ext_lower = ext.lower()
        if ext_lower in {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}:
            return cls.IMAGE
        elif ext_lower in {".pdf", ".zip", ".tar", ".gz", ".bin"}:
            return cls.BINARY
        return cls.JSON


class TaskStatus(str, Enum):
    """Status of a task in the system."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

    def __str__(self) -> str:
        return self.value


class VerificationLevel(str, Enum):
    """Level of verification to perform."""

    NONE = "none"
    BASIC = "basic"
    FULL = "full"
    STRICT = "strict"

    def __str__(self) -> str:
        return self.value
