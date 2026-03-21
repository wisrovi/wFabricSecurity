# Storage Module

**Storage backends for wFabricSecurity**

> **IMPORTANT**: View the complete Integrity Validation Matrix at **[../../../index.html](../../../index.html)** (or at https://wisrovi.github.io/wFabricSecurity/)

## Overview

This module provides storage backends for persisting data. It includes both a Hyperledger Fabric backend (primary) and a Local JSON file backend (fallback).

## Components

### FabricStorage (`fabric_storage.py`)

Blockchain-based storage using Hyperledger Fabric:

```python
from wFabricSecurity.fabric_security.storage import FabricStorage

storage = FabricStorage(gateway)

# Register participant
result = storage.register_participant({
    "identity": "CN=Master",
    "role": "worker",
    "certificate": "-----BEGIN CERTIFICATE-----..."
})

# Get participant
participant = storage.get_participant("CN=Master")

# Get certificate
cert = storage.get_certificate("CN=Master")

# Register task
result = storage.register_task(task_id, hash_a)

# Complete task
result = storage.complete_task(task_id, hash_b, signature)

# Check revoked
is_revoked = storage.is_revoked("CN=Master")
```

### LocalStorage (`local.py`)

JSON file-based fallback storage:

```python
from wFabricSecurity.fabric_security.storage import LocalStorage

storage = LocalStorage(data_dir="/tmp/security_data")

# Save data
storage.save("participant:CN=Master", participant_data)

# Get data
data = storage.get("participant:CN=Master")

# List keys
keys = storage.list_keys("participant:")

# Save message
storage.save_message(message_id, message_data, ttl_seconds=3600)

# Get message
msg = storage.get_message(message_id)

# List messages
message_ids = storage.list_keys("msg_")

# Cleanup expired
count = storage.cleanup_expired_messages()
```

## Storage Comparison

| Feature | FabricStorage | LocalStorage |
|---------|---------------|--------------|
| **Persistence** | Blockchain (immutable) | Local JSON files |
| **Availability** | Requires Fabric network | Always available |
| **Performance** | Network latency | Fast (local disk) |
| **Use Case** | Production | Development/Testing |
| **Audit Trail** | Immutable ledger | Local only |

## Automatic Fallback

The library automatically falls back to LocalStorage when Fabric is unavailable:

```python
gateway = FabricGateway(msp_path="/path/to/msp")

# If Fabric connection fails:
# - FabricStorage operations use LocalStorage
# - No code changes required
# - Automatic detection
```

## Data Organization

```
LocalStorage Directory Structure:
/tmp/security_data/
├── certs/                    # Cached certificates
│   └── {identity}.pem
├── code_hashes/             # Registered code hashes
│   └── {identity}_{version}.json
├── messages/                 # Stored messages
│   └── msg_{message_id}.json
├── participants/            # Participant data
│   └── {identity}.json
├── permissions/             # Communication permissions
│   └── {from}_{to}.json
├── revoked/                 # Revoked participants
│   └── {identity}.json
└── tasks/                   # Task records
    └── {task_id}.json
```

## TTL (Time-To-Live) Support

Messages can have automatic expiration:

```python
# Create message with TTL
storage.save_message(
    message_id="msg_123",
    message_data=message_dict,
    ttl_seconds=3600  # Expires in 1 hour
)

# Cleanup expired messages
count = storage.cleanup_expired_messages()
```

## Coverage

| File | Coverage |
|------|----------|
| fabric_storage.py | 77% |
| local.py | 95% |

## Usage in Zero Trust Flow

```
MASTER                                          SLAVE
  │                                               │
  │  Register identity in Fabric                   │
  │──────────────────────────────────────────────►│
  │                                               │
  │  Store code hash                              │
  │──────────────────────────────────────────────►│
  │                                               │
  │                            Query code hash    │
  │◄──────────────────────────────────────────────│
  │                                               │
  │                            Verify matches     │
  │                                               │
  │  Complete task (store hash_b)                 │
  │──────────────────────────────────────────────►│
  │                                               │
```
