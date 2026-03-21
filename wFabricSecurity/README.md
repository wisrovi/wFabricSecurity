# wFabricSecurity Package

**Zero Trust Security System for Hyperledger Fabric**

> **Integrity Validation Matrix**: View at **[../../index.html](../../index.html)** or **[GitHub Pages](https://wisrovi.github.io/wFabricSecurity/)**

## Overview

This package contains the core implementation of the wFabricSecurity library. It provides cryptographic security, identity management, and blockchain integration for distributed applications.

## Directory Structure

```
wFabricSecurity/
├── __init__.py              # Package exports and version
└── fabric_security/
    ├── __init__.py          # Internal module exports
    ├── config/              # Configuration management
    ├── core/                # Core data structures
    ├── crypto/              # Cryptographic services
    ├── fabric/              # Hyperledger Fabric integration
    ├── security/            # Security validations
    └── storage/             # Storage backends
```

## Quick Start

```python
from wFabricSecurity import FabricSecurity

security = FabricSecurity(
    me="Master",
    msp_path="/path/to/msp"
)

security.register_identity()
security.register_code(["master.py"], "1.0.0")

message = security.create_message(
    recipient="CN=Slave",
    content='{"operation": "process_data"}'
)

if security.verify_message(message):
    print("Message is authentic and unaltered")
```

## Core Components

| Component | Description |
|-----------|-------------|
| **FabricSecurity** | Full Zero Trust security system |
| **FabricSecuritySimple** | Simplified API for basic use |

## Documentation

- [Main README](../../README.md) - Project overview and examples
- [API Reference](../../docs/source/api_reference.rst) - Detailed API documentation
- [Tests Coverage Report](../../test/reports/) - Test integrity matrix

## License

MIT License - see [LICENSE](../../LICENSE) for details.
