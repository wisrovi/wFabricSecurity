# fabric_security

**Core library module for wFabricSecurity**

## Overview

This module contains the core implementation of the wFabricSecurity library. It provides all the security, cryptographic, and blockchain integration functionality.

## Module Structure

```
fabric_security/
├── __init__.py          # Module exports
├── fabric_security.py   # Main classes (FabricSecurity, FabricSecuritySimple)
├── cli.py               # Command-line interface
├── config/              # Configuration management
├── core/                # Core data structures
├── crypto/              # Cryptographic services
├── fabric/              # Hyperledger Fabric integration
├── security/            # Security validations
└── storage/             # Storage backends
```

## Main Classes

### FabricSecurity

Full-featured Zero Trust security system:

```python
from wFabricSecurity import FabricSecurity

security = FabricSecurity(
    me="Master",
    msp_path="/path/to/msp",
    fabric_channel="mychannel",
    fabric_chaincode="tasks"
)

# Register identity and code
security.register_identity()
security.register_code(["master.py"], "1.0.0")

# Set up permissions
security.register_communication("CN=Master", "CN=Slave")

# Create and verify messages
message = security.create_message("CN=Slave", '{"task": "process"}')
if security.verify_message(message):
    print("Message valid!")
```

### FabricSecuritySimple

Simplified API for basic use:

```python
from wFabricSecurity import FabricSecuritySimple

security = FabricSecuritySimple(me="Master")

# Use decorators for automatic security
@security.master_audit(trusted_slaves=["CN=Slave"])
def send_task(payload):
    return http_post("http://slave/process", payload)

@security.slave_verify(trusted_masters=["CN=Master"])
def process_task(payload):
    return process(payload)
```

## Security Features

| Feature | Description |
|---------|-------------|
| Code Integrity | SHA-256 hash verification |
| Digital Signatures | ECDSA P-256 |
| Permissions | Fine-grained access control |
| Message Integrity | Hash + signature verification |
| Rate Limiting | Token bucket algorithm |
| Retry Logic | Exponential backoff |

## CLI Usage

```bash
# Register identity
python -m wFabricSecurity.cli register-identity --me Master

# Register code
python -m wFabricSecurity.cli register-code --files master.py --version 1.0.0

# Check permission
python -m wFabricSecurity.cli check-permission --from CN=Master --to CN=Slave
```

## Documentation

- [Package README](../README.md) - Project overview
- [config/README.md](config/README.md) - Configuration
- [core/README.md](core/README.md) - Data structures
- [crypto/README.md](crypto/README.md) - Cryptography
- [fabric/README.md](fabric/README.md) - Fabric integration
- [security/README.md](security/README.md) - Security validations
- [storage/README.md](storage/README.md) - Storage backends

## Version

See [version info](../wFabricSecurity/__init__.py) for current version.
