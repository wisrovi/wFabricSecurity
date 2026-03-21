"""Security exceptions for wFabricSecurity."""

from typing import Optional


class SecurityError(Exception):
    """Base security exception."""

    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class CodeIntegrityError(SecurityError):
    """Raised when code integrity verification fails."""

    def __init__(
        self,
        message: str = "Code integrity verification failed. The code may have been tampered with.",
        details: Optional[dict] = None,
    ):
        super().__init__(message, details)


class PermissionDeniedError(SecurityError):
    """Raised when communication permission is denied."""

    def __init__(
        self,
        message: str = "Permission denied. The sender is not authorized to communicate with the recipient.",
        details: Optional[dict] = None,
    ):
        super().__init__(message, details)


class MessageIntegrityError(SecurityError):
    """Raised when message integrity verification fails."""

    def __init__(
        self,
        message: str = "Message integrity verification failed. The message may have been altered.",
        details: Optional[dict] = None,
    ):
        super().__init__(message, details)


class SignatureError(SecurityError):
    """Raised when signature verification fails."""

    def __init__(
        self,
        message: str = "Signature verification failed. The signature is invalid.",
        details: Optional[dict] = None,
    ):
        super().__init__(message, details)


class RateLimitError(SecurityError):
    """Raised when rate limit is exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded. Too many requests.",
        details: Optional[dict] = None,
    ):
        super().__init__(message, details)


class RevocationError(SecurityError):
    """Raised when a revoked participant is detected."""

    def __init__(
        self,
        message: str = "Participant has been revoked.",
        details: Optional[dict] = None,
    ):
        super().__init__(message, details)


class ConfigurationError(SecurityError):
    """Raised when there is a configuration error."""

    def __init__(
        self,
        message: str = "Configuration error.",
        details: Optional[dict] = None,
    ):
        super().__init__(message, details)
