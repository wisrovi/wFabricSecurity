# Examples

**Functional examples demonstrating wFabricSecurity usage**

## Overview

This directory contains complete working examples demonstrating how to use wFabricSecurity in different scenarios: JSON data processing, image handling, and P2P sensitive data.

## Directory Structure

```
examples/
├── base/                  # Synchronous examples
│   ├── master.py         # Master node implementation
│   └── slave.py          # Slave node implementation
├── async/                # Asynchronous examples
│   ├── master.py         # Async master implementation
│   └── slave.py          # Async slave implementation
├── json/                 # JSON data examples
├── image/                # Image processing examples
├── p2p/                  # P2P/sensitive data examples
├── data/                  # Binary file examples
└── test/                 # Example tests
    ├── test_json.py      # JSON tests
    ├── test_image.py     # Image tests
    ├── test_p2p.py       # P2P tests
    ├── test_core.py      # Core tests
    ├── test_security.py  # Security tests
    ├── test_zero_trust.py # Zero Trust flow tests
    └── reports/          # Generated test reports
```

## Example Types

### JSON Processing
```bash
cd examples/json/base
python master.py
# In another terminal:
python slave.py
```

### Image Processing
```bash
cd examples/image/base
python master.py --image /path/to/image.jpg
python slave.py
```

### P2P Sensitive Data
```bash
cd examples/p2p/base
python master.py --p2p '{"card": "1234-5678-9012"}'
python slave.py
```

## Running Examples

```bash
# From examples directory
cd examples

# Run all example tests
make test-all

# Run specific example tests
python -m pytest test/test_json.py -v

# View example test reports
open test/reports/
```

## Master-Slave Communication Flow

```
┌─────────────────┐                      ┌─────────────────┐
│      MASTER     │                      │      SLAVE      │
│                 │                      │                 │
│ 1. Load config │                      │ 1. Load config  │
│ 2. Register ID  │                      │ 2. Register ID  │
│ 3. Set up comms │ ──────────────────────│ 3. Verify comms  │
│ 4. Create task  │   POST {payload,     │ 4. Verify sig   │
│ 5. Sign hash_a  │       hash_a, sig}   │ 5. Check perm   │
│ 6. Send request │◄─────────────────────│ 6. Process task │
│ 7. Wait result  │   Response {result,  │ 7. Sign hash_b  │
│ 8. Verify sig   │       hash_b, sig}   │ 8. Send result  │
│ 9. Store hash_a │ ──────────────────────│ 9. Store hash_b │
└─────────────────┘                      └─────────────────┘
```

## Key Features Demonstrated

| Example | Features Shown |
|---------|---------------|
| JSON | Message creation, JSON serialization, signature verification |
| Image | Binary data handling, base64 encoding, large payload processing |
| P2P | Sensitive data masking, restricted permissions, encrypted storage |

## Testing Examples

```bash
# Run example-specific tests
cd examples
make test-json
make test-image
make test-p2p

# Generate test report
make report
```

## Configuration

Examples use default settings but can be customized:

```python
security = FabricSecurity(
    me="Master",
    msp_path="/path/to/msp",
    fabric_channel="mychannel",
    fabric_chaincode="tasks"
)
```
