<p align="center">
  <a href="https://pypi.org/project/wFabricSecurity/"><img src="https://img.shields.io/pypi/v/wFabricSecurity?style=for-the-badge&logo=pypi&color=3b82f6" alt="PyPI version" /></a>
  <a href="https://linkedin.com/in/wisrovi-rodriguez"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn" /></a>
  <a href="https://wisrovi.dev"><img src="https://img.shields.io/badge/Author-wisrovi.dev-111827?style=for-the-badge&logo=google-chrome&logoColor=white" alt="Portal" /></a>
  <a href="https://orcid.org/0009-0005-0710-1861"><img src="https://img.shields.io/badge/ORCID-0009--0005--0710--1861-A6CE39?style=for-the-badge&logo=orcid&logoColor=white" alt="ORCID" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge" alt="License" /></a>
  <a href="https://wFabricSecurity.readthedocs.io/en/latest/"><img src="https://img.shields.io/readthedocs/wfabricsecurity/latest?style=for-the-badge" alt="Documentation" /></a>
</p>

# wFabricSecurity

**Zero Trust Security System for Hyperledger Fabric**

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

## Author & Research Affiliation

* **William Steve Rodriguez Villamizar (Wisrovi)**
* **Role:** Principal AI Engineer & Applied AI Solutions Architect | Scientific Researcher
* 🌐 **Official Portal:** [wisrovi.dev](https://wisrovi.dev)
* 💼 **LinkedIn:** [wisrovi-rodriguez](https://www.linkedin.com/in/wisrovi-rodriguez/)
* 🆔 **ORCID:** [0009-0005-0710-1861](https://orcid.org/0009-0005-0710-1861)
* 📦 **PyPI:** [pypi.org/user/wisrovi/](https://pypi.org/user/wisrovi/)
* 🐙 **GitHub:** [@wisrovi](https://github.com/wisrovi)
* 📧 **Email:** wisrovi@wisrovi.dev

---

## Links

| Resource | URL |
|----------|-----|
| **PyPI** | https://pypi.org/project/wFabricSecurity/ |
| **Documentation** | https://wFabricSecurity.readthedocs.io/en/latest/ |
| **GitHub** | https://github.com/wisrovi/wFabricSecurity/ |
| **Issues** | https://github.com/wisrovi/wFabricSecurity/issues |
