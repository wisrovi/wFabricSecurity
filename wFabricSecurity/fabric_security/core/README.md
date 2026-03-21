# Core Module

**Core data structures and types for wFabricSecurity**

> **IMPORTANT**: View the complete Integrity Validation Matrix at **[../../../index.html](../../../index.html)** (or at https://wisrovi.github.io/wFabricSecurity/)

## Overview

This module contains the fundamental data structures, enumerations, and exception types used throughout the library.

## Contents

### Exceptions (`exceptions.py`)

8 security exception types for Zero Trust validation:

| Exception | Description |
|-----------|-------------|
| `SecurityError` | Base security exception |
| `CodeIntegrityError` | Code hash mismatch (tampering detected) |
| `PermissionDeniedError` | Communication not allowed |
| `MessageIntegrityError` | Message content modified |
| `SignatureError` | Invalid cryptographic signature |
| `RateLimitError` | Too many requests |
| `RevocationError` | Participant has been revoked |
| `ConfigurationError` | Invalid configuration |

### Models (`models.py`)

Core data models:

| Model | Description |
|-------|-------------|
| `Message` | Signed message with sender, recipient, content, hash, signature, TTL |
| `Participant` | Identity with role, certificate, permissions |
| `Task` | Task record with hash_a, hash_b, status |

### Enums (`enums.py`)

Type enumerations:

| Enum | Values |
|------|--------|
| `CommunicationDirection` | OUTBOUND, INBOUND, BIDIRECTIONAL |
| `DataType` | JSON, IMAGE, P2P, BINARY |
| `ParticipantStatus` | ACTIVE, INACTIVE, REVOKED, SUSPENDED |
| `TaskStatus` | PENDING, IN_PROGRESS, COMPLETED, FAILED, CANCELLED |
| `VerificationLevel` | NONE, BASIC, FULL, STRICT |

## Usage Example

```python
from wFabricSecurity.fabric_security.core import (
    Message,
    Participant,
    ParticipantRole,
    CodeIntegrityError,
)

# Create a message
msg = Message(
    sender="CN=Master",
    recipient="CN=Slave",
    content='{"task": "process"}',
    content_hash="sha256:abc123...",
    signature="base64:signature...",
    timestamp=datetime.now().isoformat(),
)

# Handle exceptions
try:
    verify_code(code_path)
except CodeIntegrityError:
    print("Code has been tampered with!")
```

## Coverage

| File | Coverage |
|------|----------|
| exceptions.py | 100% |
| models.py | 96% |
| enums.py | 91% |

See [tests](../../test/test_library.py) for detailed test coverage.
