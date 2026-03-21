# wFabricSecurity

**Zero Trust Security System for Hyperledger Fabric**

[![Python Version](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![PyPI Version](https://img.shields.io/pypi/v/wFabricSecurity.svg)](https://pypi.org/project/wFabricSecurity/)
[![Documentation](https://img.shields.io/readthedocs/wfabricsecurity/latest?style=flat)](https://wFabricSecurity.readthedocs.io/en/latest/)

---

## Overview

**wFabricSecurity** is a comprehensive Zero Trust Security System designed for Hyperledger Fabric environments. This library implements cryptographic identity verification, code integrity validation, communication permissions, message integrity checks, rate limiting, and retry mechanisms.

### Core Philosophy

In a Zero Trust architecture:
- **Never Trust, Always Verify** - Every request must be authenticated and authorized
- **Least Privilege** - Participants only have permissions they explicitly need
- **Assume Breach** - All communications are encrypted and verified

---

## Key Features

| Feature | Description |
|---------|-------------|
| **Code Integrity** | SHA-256 hash verification of source code to detect tampering |
| **Digital Signatures** | ECDSA P-256 cryptographic signatures for message authentication |
| **Access Control** | Zero Trust communication permissions defining who can communicate with whom |
| **Message Integrity** | Hash verification for transmission integrity with TTL support |
| **Rate Limiting** | Token bucket algorithm for DoS protection |
| **Retry Logic** | Exponential backoff ensures reliable communication |
| **Certificate Caching** | LRU cache with TTL for performance optimization |

---

## Installation

```bash
pip install wFabricSecurity
```

### Requirements

- Python 3.10 or higher
- cryptography >= 41.0.0
- ecdsa >= 0.18.0
- requests >= 2.31.0
- pyyaml >= 6.0.1

---

## Quick Start

```python
from wFabricSecurity import FabricSecurity

# Initialize security system
security = FabricSecurity(
    me="Master",
    msp_path="/path/to/msp"
)

# Register identity and code
security.register_identity()
security.register_code(["master.py"], "1.0.0")

# Register communication permissions
security.register_communication("CN=Master", "CN=Slave")

# Create and verify signed message
message = security.create_message(
    recipient="CN=Slave",
    content='{"operation": "process_data"}'
)

if security.verify_message(message):
    print("Message verified successfully!")
```

---

## Architecture

The library follows a layered modular architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│              CLI Tool          API Gateway                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                         │
│         FabricSecurity        FabricSecuritySimple           │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌────────────────┐  ┌────────────────┐  ┌────────────────────┐
│ IntegrityVerifier│  │PermissionManager│  │  MessageManager   │
└────────┬───────┘  └────────────────┘  └────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│                   CRYPTOGRAPHIC LAYER                       │
│   HashingService        SigningService       IdentityManager │
└─────────────────────────────────────────────────────────────┘
```

---

## Security Flow

```
MASTER                           SLAVE                            FABRIC
   │                               │                                 │
   │  1. Compute SHA-256 hash_a   │                                 │
   │───────────────────────────────│                                 │
   │  2. Sign hash_a (ECDSA)       │                                 │
   │───────────────────────────────│                                 │
   │  3. POST {payload, hash_a, sig} ─────►│                        │
   │                               │ 4. Verify ECDSA signature       │
   │                               │────────────────────────────────│
   │                               │ 5. Check permission table      │
   │                               │────────────────────────────────│
   │                               │ 6. Query code_hash ──────────►│
   │                               │                    7. Get data │
   │                               │◄────────────────────── 8. Return│
   │                               │                                 │
   │                    ┌──────────┴──────────┐                     │
   │                    │   CODE VALID?       │                     │
   │                    └──────────┬──────────┘                     │
   │                    YES        │        NO                       │
   │                    │          │                                 │
   │◄──────────────────┘          │ 9. Raise CodeIntegrityError    │
   │  10. Process task           │                                 │
   │──────────────────────────────►│                                 │
   │  11. Response {result, hash_b} ◄─────────────────────────────│
```

---

## Components

### Security Services

| Service | Description |
|---------|-------------|
| `IntegrityVerifier` | Verifies code integrity using SHA-256 hashing |
| `PermissionManager` | Manages communication permissions between participants |
| `MessageManager` | Handles secure message creation, signing, and verification |
| `RateLimiter` | Token bucket algorithm for DoS protection |
| `RetryLogic` | Exponential backoff retry decorator |

### Cryptographic Services

| Service | Algorithm | Purpose |
|---------|-----------|---------|
| `HashingService` | SHA-256, BLAKE2 | Code and message integrity |
| `SigningService` | ECDSA P-256 | Digital signatures |
| `IdentityManager` | X.509 | Certificate management with caching |

### Fabric Integration

| Component | Description |
|-----------|-------------|
| `FabricGateway` | Main Fabric blockchain gateway |
| `FabricNetwork` | Network abstraction layer |
| `FabricContract` | Chaincode function interface |

---

## Use Cases

| Industry | Application |
|----------|-------------|
| **Healthcare** | Secure patient data exchange between hospitals |
| **Finance** | Regulatory compliance with tamper-proof audit trails |
| **Supply Chain** | Product tracking with integrity-verified smart contracts |
| **Government** | Zero Trust architecture for citizen services |
| **IoT** | Device authentication and secure communication |

---

## Documentation

**📚 Complete documentation available at: [https://wFabricSecurity.readthedocs.io/en/latest/](https://wFabricSecurity.readthedocs.io/en/latest/)**

Includes:
- Installation guide
- API reference
- Step-by-step tutorials
- Architecture diagrams
- FAQ

---

## License

MIT License - Copyright (c) 2026 William Rodriguez

See [LICENSE](LICENSE) for details.

---

## Author

**William Rodriguez**
- GitHub: [github.com/wisrovi](https://github.com/wisrovi)
- LinkedIn: [linkedin.com/in/wisrovi-rodriguez](https://es.linkedin.com/in/wisrovi-rodriguez)
- Email: william.rodriguez@ecapturedtech.com

---

## Links

| Resource | URL |
|----------|-----|
| **PyPI** | https://pypi.org/project/wFabricSecurity/ |
| **Documentation** | https://wFabricSecurity.readthedocs.io/en/latest/ |
| **GitHub** | https://github.com/wisrovi/wFabricSecurity/ |
| **Issues** | https://github.com/wisrovi/wFabricSecurity/issues |
