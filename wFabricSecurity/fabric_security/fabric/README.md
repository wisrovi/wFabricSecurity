# Fabric Integration Module

**Hyperledger Fabric blockchain integration for wFabricSecurity**

## Overview

This module provides integration with Hyperledger Fabric blockchain for immutable audit trails, participant registration, and code hash storage.

## Components

### FabricGateway (`gateway.py`)

Main entry point for Fabric interactions:

```python
from wFabricSecurity.fabric_security.fabric import FabricGateway

gateway = FabricGateway(
    msp_path="/path/to/msp",
    channel="mychannel",
    chaincode="tasks"
)

# Get certificate
cert = gateway.get_certificate_pem("CN=Master")

# Register identity
gateway.register_identity("CN=Master", certificate_pem)

# Verify communication permission
can_communicate = gateway.verify_communication_permission("CN=Master", "CN=Slave")

# Store data in Fabric
gateway.invoke_chaincode("RegisterTask", task_id, hash_a, signature)

# Query data from Fabric
result = gateway.query_chaincode("GetTask", task_id)
```

### FabricNetwork (`network.py`)

Fabric network abstraction:

```python
from wFabricSecurity.fabric_security.fabric import FabricNetwork

network = FabricNetwork(
    peer_url="localhost:7051",
    orderer_url="orderer:7050",
    channel="mychannel"
)
```

### FabricContract (`contract.py`)

Chaincode function interface:

```python
from wFabricSecurity.fabric_security.fabric import FabricContract

contract = FabricContract(gateway)
result = contract.register_participant(participant_data)
result = contract.get_participant(identity)
result = contract.complete_task(task_id, hash_b, signature)
```

## Fabric Operations

| Operation | Chaincode Function | Description |
|-----------|-------------------|-------------|
| Register Participant | `RegisterParticipant` | Register identity in Fabric |
| Get Participant | `GetParticipant` | Query participant data |
| Register Task | `RegisterTask` | Store task hash_a |
| Complete Task | `CompleteTask` | Store task hash_b |
| Get Task | `GetTask` | Query task data |
| Verify Code | `GetCodeHash` | Retrieve registered code hash |

## Data Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         FABRIC INTEGRATION                              │
└─────────────────────────────────────────────────────────────────────────┘

    Application                    FabricGateway                    Fabric
       │                               │                              │
       │  register_identity()          │                              │
       │───────────────────────────────►│  RegisterParticipant()       │
       │                               │──────────────────────────────►│
       │                               │◄─────────────────────────────│
       │                               │  TX Result                   │
       │                               │                              │
       │  invoke_chaincode()           │                              │
       │───────────────────────────────►│  invoke()                   │
       │                               │──────────────────────────────►│
       │                               │◄─────────────────────────────│
       │                               │  TX Confirmed                │
       │                               │                              │
       │  query_chaincode()            │                              │
       │───────────────────────────────►│  query()                    │
       │                               │──────────────────────────────►│
       │                               │◄─────────────────────────────│
       │                               │  Query Result                │
```

## TLS Configuration

```python
gateway = FabricGateway(
    msp_path="/path/to/msp",
    tls_enabled=True,
    tls_ca_file="/path/to/ca.crt"
)
```

## Coverage

| File | Coverage |
|------|----------|
| gateway.py | 78% |
| network.py | 95% |
| contract.py | 73% |

## Offline Mode

When Fabric is unavailable, the library automatically falls back to LocalStorage:

```python
gateway = FabricGateway(msp_path="/path/to/msp")
# If Fabric connection fails, uses LocalStorage automatically
```
