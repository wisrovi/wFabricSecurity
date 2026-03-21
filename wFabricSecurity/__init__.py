"""
wFabricSecurity - Zero Trust Security System for Hyperledger Fabric

A complete distributed security system with cryptographic identity, code integrity
verification, communication permissions, message validation, and immutable audit.
"""

from .fabric_security import (
    FabricContract,
    FabricGateway,
    FabricNetwork,
    FabricSecurity,
    FabricSecuritySimple,
)
from .fabric_security.config import Settings, get_settings
from .fabric_security.core import (
    CodeIntegrityError,
    CommunicationDirection,
    ConfigurationError,
    DataType,
    Message,
    MessageIntegrityError,
    Participant,
    ParticipantStatus,
    PermissionDeniedError,
    RateLimitError,
    RevocationError,
    SecurityError,
    SignatureError,
    Task,
    TaskStatus,
    VerificationLevel,
)
from .fabric_security.crypto import HashingService, IdentityManager, SigningService
from .fabric_security.security import (
    IntegrityVerifier,
    MessageManager,
    PermissionManager,
    RateLimiter,
    master_audit,
    slave_verify,
    with_retry,
)
from .fabric_security.security.retry import RetryContext
from .fabric_security.storage import FabricStorage, LocalStorage

__version__ = "1.0.0"

__all__ = [
    "FabricSecurity",
    "FabricSecuritySimple",
    "FabricGateway",
    "FabricNetwork",
    "FabricContract",
    "SecurityError",
    "CodeIntegrityError",
    "PermissionDeniedError",
    "MessageIntegrityError",
    "SignatureError",
    "RateLimitError",
    "RevocationError",
    "ConfigurationError",
    "CommunicationDirection",
    "ParticipantStatus",
    "DataType",
    "TaskStatus",
    "VerificationLevel",
    "Participant",
    "Message",
    "Task",
    "HashingService",
    "SigningService",
    "IdentityManager",
    "IntegrityVerifier",
    "PermissionManager",
    "MessageManager",
    "RateLimiter",
    "with_retry",
    "master_audit",
    "slave_verify",
    "Settings",
    "get_settings",
    "LocalStorage",
    "FabricStorage",
    "RetryContext",
]
