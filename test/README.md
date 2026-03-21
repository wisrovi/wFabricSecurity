# Test Suite

**Unit tests for wFabricSecurity library**

## Overview

This directory contains the comprehensive test suite for the wFabricSecurity library with 258 unit tests achieving 85% code coverage.

## Files

| File | Description |
|------|-------------|
| `test_library.py` | Main test suite (258 tests) |
| `test_report_generator.py` | HTML report generator |
| `reports/` | Generated test reports |

## Running Tests

```bash
# Run all tests
python -m pytest test/test_library.py -v

# Run with coverage
python -m pytest test/test_library.py --cov=wFabricSecurity --cov-report=html

# Run specific test class
python -m pytest test/test_library.py::TestCoreExceptions -v

# Run with verbose output
python -m pytest test/test_library.py -vv
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

### Core Tests
- `TestCoreExceptions` - Exception handling
- `TestCoreEnums` - Enumeration values
- `TestCoreModels` - Data model serialization

### Configuration Tests
- `TestConfigSettings` - Settings loading
- `TestConfigDefaults` - Default values

### Crypto Tests
- `TestHashingService` - Hash computation
- `TestSigningService` - Signing/verification
- `TestIdentityManager` - Certificate management

### Fabric Tests
- `TestFabricGateway` - Gateway operations
- `TestFabricNetwork` - Network configuration
- `TestFabricContract` - Chaincode interface

### Security Tests
- `TestIntegrityVerifier` - Code integrity
- `TestPermissionManager` - Access control
- `TestMessageManager` - Message handling
- `TestRateLimiter` - Rate limiting
- `TestRetryLogic` - Retry mechanisms

### Storage Tests
- `TestLocalStorage` - Local file storage
- `TestFabricStorage` - Blockchain storage

## Generating Reports

```bash
# Generate integrity validation matrix report
python test/test_report_generator.py

# Generate coverage HTML report
python -m pytest test/test_library.py --cov=wFabricSecurity --cov-report=html

# Open reports
firefox test/reports/library_test_report_*.html
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
python -m pytest test/test_library.py -q

# Run with coverage summary
python -m pytest test/test_library.py --cov=wFabricSecurity --cov-report=term

# Run only failed tests from last run
python -m pytest test/test_library.py --lf
```
