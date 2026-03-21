"""
wFabricSecurity - Zero Trust Security System for Hyperledger Fabric

A complete distributed security system with cryptographic identity, code integrity
verification, communication permissions, message validation, and immutable audit.
"""

from .fabric_security import (
    FabricSecurity,
    FabricSecuritySimple,
    FabricGateway,
    FabricNetwork,
    FabricContract,
)

from .fabric_security.core import (
    SecurityError,
    CodeIntegrityError,
    PermissionDeniedError,
    MessageIntegrityError,
    SignatureError,
    RateLimitError,
    RevocationError,
    ConfigurationError,
    CommunicationDirection,
    ParticipantStatus,
    DataType,
    TaskStatus,
    VerificationLevel,
    Participant,
    Message,
    Task,
)

from .fabric_security.crypto import (
    HashingService,
    SigningService,
    IdentityManager,
)

from .fabric_security.security import (
    IntegrityVerifier,
    PermissionManager,
    MessageManager,
    RateLimiter,
    with_retry,
    master_audit,
    slave_verify,
)

from .fabric_security.config import Settings, get_settings

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
]
