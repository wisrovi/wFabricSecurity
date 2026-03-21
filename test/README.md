# Test Suite

**Unit tests for wFabricSecurity library**

> **IMPORTANT**: View the complete Integrity Validation Matrix at **[../index.html](../index.html)** (or at https://wisrovi.github.io/wFabricSecurity/)

## Overview

This directory contains the comprehensive test suite for the wFabricSecurity library with 112 unit tests achieving 85% code coverage. The tests are split into modular files for better organization and maintainability.

## Files

| File | Description |
|------|-------------|
| `conftest.py` | Shared pytest fixtures |
| `test_main.py` | Main classes and version tests |
| `test_core.py` | Core exceptions, enums, models |
| `test_config.py` | Settings configuration |
| `test_crypto.py` | Hashing, signing, identity |
| `test_fabric.py` | Gateway, network, contract |
| `test_security.py` | Integrity, permissions, messages |
| `test_rate_retry.py` | Rate limiter, retry logic |
| `test_storage.py` | Local storage, fabric storage |
| `test_report_generator.py` | HTML report generator |
| `reports/` | Generated test reports |

## Running Tests

```bash
# Run all tests
python -m pytest test/ -v

# Run with coverage
python -m pytest test/ --cov=wFabricSecurity --cov-report=html

# Run specific test file
python -m pytest test/test_core.py -v

# Run specific test class
python -m pytest test/test_core.py::TestCoreExceptions -v

# Run with verbose output
python -m pytest test/ -vv
```

## Test Coverage

| Module | Coverage |
|--------|----------|
| config | 94-100% |
| core | 91-100% |
| crypto | 75-91% |
| fabric | 73-95% |
| security | 78-89% |
| storage | 77-95% |
| **Overall** | **85%** |

## Test Categories

### Core Tests (test_core.py)
- `TestCoreExceptions` - Exception handling (8 exceptions)
- `TestCoreEnums` - Enumeration values
- `TestCoreModels` - Data model serialization

### Configuration Tests (test_config.py)
- `TestConfigSettings` - Settings loading from YAML
- `TestConfigDefaults` - Default values

### Crypto Tests (test_crypto.py)
- `TestHashingService` - SHA-256, BLAKE2 hashing
- `TestSigningService` - ECDSA signing/verification
- `TestIdentityManager` - X.509 certificate management

### Fabric Tests (test_fabric.py)
- `TestFabricGateway` - Gateway operations
- `TestFabricNetwork` - Network configuration
- `TestFabricContract` - Chaincode interface

### Security Tests (test_security.py)
- `TestIntegrityVerifier` - Code integrity validation
- `TestPermissionManager` - Access control
- `TestMessageManager` - Message handling with TTL

### Rate & Retry Tests (test_rate_retry.py)
- `TestRateLimiter` - Token bucket algorithm
- `TestRetryLogic` - Exponential backoff

### Storage Tests (test_storage.py)
- `TestLocalStorage` - Local JSON file storage
- `TestFabricStorage` - Blockchain storage backend

## Generating Reports

```bash
# Generate integrity validation matrix report
python test/test_report_generator.py

# Generate coverage HTML report
python -m pytest test/ --cov=wFabricSecurity --cov-report=html

# Open reports
firefox ../index.html
firefox htmlcov/index.html
```

## Test Philosophy

- **No Mocks for Core Logic**: Real cryptographic operations when possible
- **Integration Tests**: End-to-end validation of Zero Trust flow
- **Exception Handling**: Verify correct exceptions are raised
- **Edge Cases**: Empty inputs, expired messages, revoked participants

## Quick Test Commands

```bash
# Run quick test
python -m pytest test/ -q

# Run with coverage summary
python -m pytest test/ --cov=wFabricSecurity --cov-report=term

# Run only failed tests from last run
python -m pytest test/ --lf
```
