# Configuration Module

**Settings management for wFabricSecurity**

> **Integrity Validation Matrix**: View at **[../../../index.html](../../../index.html)** or **[GitHub Pages](https://wisrovi.github.io/wFabricSecurity/)**

## Overview

This module handles all configuration for the library, supporting both YAML files and environment variables with automatic fallback to defaults.

## Files

| File | Description |
|------|-------------|
| `settings.py` | Settings class with YAML/env/defaults support |
| `defaults.py` | Default configuration values |

## Configuration Sources

Settings are loaded in this priority order:
1. Environment variables (highest priority)
2. YAML configuration file
3. Default values (lowest priority)

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FABRIC_LOCAL_DATA_DIR` | `/tmp/fabric_security` | Local data storage path |
| `FABRIC_PEER_URL` | `localhost:7051` | Fabric peer gRPC URL |
| `FABRIC_ORDERER_URL` | `orderer.net:7050` | Fabric orderer URL |
| `FABRIC_CHANNEL` | `mychannel` | Fabric channel name |
| `FABRIC_CHAINCODE` | `tasks` | Chaincode name |
| `FABRIC_MSP_PATH` | *(auto-detect)* | Path to MSP directory |
| `FABRIC_TLS_ENABLED` | `false` | Enable TLS |
| `FABRIC_RATE_LIMIT_RPS` | `100` | Requests per second |
| `FABRIC_RETRY_MAX_ATTEMPTS` | `3` | Max retry attempts |
| `FABRIC_LOG_LEVEL` | `INFO` | Logging level |

## Usage

```python
from wFabricSecurity import Settings

# Load from environment
settings = Settings.from_env()

# Load from YAML file
settings = Settings.from_yaml("config.yaml")

# Access configuration
print(settings.fabric_channel)  # mychannel
print(settings.rate_limit_requests_per_second)  # 100
```

## YAML Configuration Example

```yaml
local_data_dir: /custom/path
fabric_channel: custom_channel
fabric_chaincode: mychaincode
fabric_peer_url: peer.example.com:7051
rate_limit_rps: 200
retry_max_attempts: 5
message_ttl_seconds: 7200
```

## Singleton Pattern

The library provides a global settings instance:

```python
from wFabricSecurity import get_settings, configure_settings

# Get global settings
settings = get_settings()

# Override global settings
custom_settings = Settings.from_yaml("prod.yaml")
configure_settings(custom_settings)
```

## Coverage

| File | Coverage |
|------|----------|
| settings.py | 94% |
| defaults.py | 100% |
