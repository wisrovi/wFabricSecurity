# Security Module

**Zero Trust security validations for wFabricSecurity**

## Overview

This module implements the core security validations for the Zero Trust model. Each validation type ensures specific security properties are maintained.

## Components

### IntegrityVerifier (`integrity.py`)

Verifies source code has not been tampered with:

```python
from wFabricSecurity.fabric_security.security import IntegrityVerifier

verifier = IntegrityVerifier(gateway)

# Register code hash
verifier.register_code(["master.py"], "1.0.0")

# Verify code integrity
is_valid = verifier.verify_code(["master.py"])

# Verify multiple files
results = verifier.verify_code_integrity(["file1.py", "file2.py"], expected_hash)
```

### PermissionManager (`permissions.py`)

Fine-grained access control:

```python
from wFabricSecurity.fabric_security.security import PermissionManager
from wFabricSecurity import CommunicationDirection

permissions = PermissionManager(gateway)

# Register permission
permissions.register_communication(
    from_identity="CN=Master",
    to_identity="CN=Slave",
    direction=CommunicationDirection.BIDIRECTIONAL
)

# Check permission
can_communicate = permissions.can_communicate_with("CN=Master", "CN=Slave")

# Revoke participant
permissions.revoke_participant("CN=BadActor")
```

### MessageManager (`messages.py`)

Message creation with integrity and TTL:

```python
from wFabricSecurity.fabric_security.security import MessageManager
from wFabricSecurity import DataType

messages = MessageManager(gateway, ttl_seconds=3600)

# Create text message
msg = messages.create_message(
    sender="CN=Master",
    recipient="CN=Slave",
    content="sensitive data"
)

# Create JSON message
msg = messages.create_json_message(
    sender="CN=Master",
    recipient="CN=Slave",
    data={"operation": "process", "data": "value"}
)

# Verify message
is_valid = messages.verify_message(msg)

# Cleanup expired
count = messages.cleanup_expired()
```

### RateLimiter (`rate_limiter.py`)

Token bucket rate limiting:

```python
from wFabricSecurity.fabric_security.security import RateLimiter

limiter = RateLimiter(requests_per_second=100, burst=50)

# Acquire token (blocks if unavailable)
limiter.acquire()

# Try acquire (non-blocking)
if limiter.try_acquire():
    process_request()
else:
    raise RateLimitError("Too many requests")
```

### Retry Logic (`retry.py`)

Exponential backoff retry:

```python
from wFabricSecurity.fabric_security.security import with_retry, RetryContext

# Decorator
@with_retry(max_attempts=3, backoff_factor=2.0, initial_delay=0.5)
def unreliable_call():
    return fabric_invoke()

# Context manager
ctx = RetryContext(max_attempts=3, initial_delay=0.5)
with ctx:
    result = potentially_failing_operation()
```

### Decorators (`decorators.py`)

High-level security decorators:

```python
from wFabricSecurity.fabric_security.security import master_audit, slave_verify

# Master decorator - automatically signs and audits
@master_audit(trusted_slaves=["CN=Slave1", "CN=Slave2"])
def send_task(payload, task_id, hash_a, sig, my_id):
    return http_post("http://slave/process", payload)

# Slave decorator - verifies incoming requests
@slave_verify(trusted_masters=["CN=Master"])
def process_task(payload):
    return process(payload)
```

## Zero Trust Validations

| Validation | Description | Raises |
|------------|-------------|--------|
| **Code Integrity** | SHA-256 hash verification | CodeIntegrityError |
| **Permission Check** | Access control verification | PermissionDeniedError |
| **Message Integrity** | Content hash verification | MessageIntegrityError |
| **Signature Verification** | ECDSA signature check | SignatureError |
| **Rate Limiting** | Token bucket enforcement | RateLimitError |
| **Revocation Check** | Participant status | RevocationError |

## Validation Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      ZERO TRUST VALIDATION FLOW                          │
└─────────────────────────────────────────────────────────────────────────┘

    Incoming Request
           │
           ▼
    ┌──────────────────┐
    │ 1. Verify        │ ◄── Extract certificate, verify ECDSA signature
    │    Signature      │
    └────────┬─────────┘
             │
     ┌───────┴───────┐
     │ Valid?        │
     └───┬───────┬───┘
        YES        NO
         │          │
         ▼          ▼
   ┌───────────┐  ┌────────────┐
   │ 2. Check  │  │ REJECT     │
   │ Permission │  │ SignatureError
   └─────┬─────┘
         │
   ┌─────┴─────┐
   │ Allowed?   │
   └───┬─────┬─┘
      YES     NO
       │       │
       ▼       ▼
 ┌─────────┐ ┌────────────┐
 │ 3. Check│ │  REJECT    │
 │ Code    │ │ Permission │
 │ Integrity│ │ DeniedError│
 └────┬────┘
      │
┌─────┴─────┐
│ Code      │
│ Valid?    │
└─┬─────┬───┘
  YES    NO
   │      │
   ▼      ▼
┌──────┐ ┌────────────────┐
│ALLOW│ │ REJECT         │
│     │ │ CodeIntegrity  │
└──────┘ │ Error          │
         └────────────────┘
```

## Coverage

| File | Coverage |
|------|----------|
| integrity.py | 78% |
| permissions.py | 89% |
| messages.py | 86% |
| rate_limiter.py | 88% |
| retry.py | 78% |
| decorators.py | N/A |
