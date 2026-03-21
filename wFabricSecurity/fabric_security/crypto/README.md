# Cryptographic Services Module

**Hashing, signing, and identity management for wFabricSecurity**

> **Integrity Validation Matrix**: View at **[../../../index.html](../../../index.html)** or **[GitHub Pages](https://wisrovi.github.io/wFabricSecurity/)**

## Overview

This module provides the cryptographic foundation for the Zero Trust security system, including SHA-256/BLAKE2 hashing, ECDSA signing/verification, and X.509 certificate management.

## Components

### HashingService (`hashing.py`)

Cryptographic hash computation:

| Algorithm | Output Size | Use Case |
|-----------|-------------|----------|
| SHA-256 | 256 bits | Default for all hashing |
| SHA-384 | 384 bits | High security |
| SHA-512 | 512 bits | Very high security |
| BLAKE2 | 256/512 bits | Fast, secure alternative |

```python
from wFabricSecurity.fabric_security.crypto import HashingService

hasher = HashingService()
hash_result = hasher.hash("data", algorithm="sha256")
# Returns: "sha256:aec070645fe53ee3b3763059376134f058cc337247c978add178b6ccdfb0019f"
```

### SigningService (`signing.py`)

Digital signature generation and verification:

```python
from wFabricSecurity.fabric_security.crypto import SigningService

signer = SigningService(msp_path="/path/to/msp")

# Sign data (uses ECDSA P-256)
signature = signer.sign("data to sign", "CN=Master")

# Verify signature
is_valid = signer.verify("data", signature, "CN=Master")

# HMAC fallback when private key unavailable
hmac_signature = signer.sign_hmac("data", "secret_key")
```

### IdentityManager (`identity.py`)

X.509 certificate management with LRU cache:

```python
from wFabricSecurity.fabric_security.crypto import IdentityManager

identity_mgr = IdentityManager(msp_path="/path/to/msp")

# Get certificate PEM
cert_pem = identity_mgr.get_certificate_pem("CN=Master")

# Get signer ID (Common Name)
signer_id = identity_mgr.get_signer_id()

# Clear certificate cache
identity_mgr.clear_cache()
```

## Cryptographic Algorithms

| Service | Algorithm | Curve/Key |
|---------|-----------|-----------|
| Hashing | SHA-256, SHA-384, SHA-512, BLAKE2 | N/A |
| Signing | ECDSA | P-256 curve |
| HMAC | HMAC-SHA256 | Fallback |
| Certificates | X.509 | RSA/ECDSA |

## Security Properties

- **Collision Resistance**: SHA-256/BLAKE2 provide strong collision resistance
- **Signature Non-Repudiation**: ECDSA signatures prove identity
- **Certificate Validation**: X.509 chain verification
- **Cache Security**: Certificate cache with TTL prevents stale data

## Coverage

| File | Coverage |
|------|----------|
| hashing.py | 91% |
| signing.py | 77% |
| identity.py | 75% |

## Usage in Zero Trust Flow

```
1. MASTER computes SHA-256 hash of payload
         │
         ▼
2. MASTER signs hash with ECDSA private key
         │
         ▼
3. SLAVE extracts MASTER certificate from MSP
         │
         ▼
4. SLAVE verifies ECDSA signature using certificate
         │
         ▼
5. If valid → Process request
   If invalid → Reject with SignatureError
```
