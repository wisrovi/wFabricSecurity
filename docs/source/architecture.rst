.. _architecture:

##########
Architecture
##########

This section provides an in-depth look at the wFabricSecurity architecture, design patterns, and implementation details.

|

.. contents::
   :local:
   :depth: 3

|

----

|

.. _arch-overview:

========
Overview
========

wFabricSecurity is built on a **layered architecture** that separates concerns and provides modular, testable components:

|

.. graphviz::

    digraph LayeredArchitecture {
        rankdir=TB;
        size="8,10";
        
        subgraph cluster_presentation {
            label="Presentation Layer";
            style="rounded";
            color="#667eea";
            fontcolor="#667eea";
            node [style="filled,rounded", fillcolor="#E3F2FD"];
            CLI ["CLI Tool"];
            API ["API Gateway"];
        }
        
        subgraph cluster_application {
            label="Application Layer";
            style="rounded";
            color="#764ba2";
            fontcolor="#764ba2";
            node [style="filled,rounded", fillcolor="#F3E5F5"];
            FS ["FabricSecurity"];
            FSS ["FabricSecuritySimple"];
        }
        
        subgraph cluster_security {
            label="Security Services Layer";
            style="rounded";
            color="#4CAF50";
            fontcolor="#4CAF50";
            node [style="filled,rounded", fillcolor="#E8F5E9"];
            IV ["IntegrityVerifier"];
            PM ["PermissionManager"];
            MM ["MessageManager"];
            RL ["RateLimiter"];
        }
        
        subgraph cluster_crypto {
            label="Cryptographic Layer";
            style="rounded";
            color="#FF9800";
            fontcolor="#FF9800";
            node [style="filled,rounded", fillcolor="#FFF3E0"];
            HS ["HashingService"];
            SS ["SigningService"];
            IM ["IdentityManager"];
        }
        
        subgraph cluster_fabric {
            label="Hyperledger Fabric Layer";
            style="rounded";
            color="#2196F3";
            fontcolor="#2196F3";
            node [style="filled,rounded", fillcolor="#E3F2FD"];
            GW ["FabricGateway"];
            NW ["FabricNetwork"];
            CT ["FabricContract"];
        }
        
        subgraph cluster_storage {
            label="Storage Layer";
            style="rounded";
            color="#607D8B";
            fontcolor="#607D8B";
            node [style="filled,rounded", fillcolor="#ECEFF1"];
            LS ["LocalStorage"];
            FSs ["FabricStorage"];
        }
        
        CLI -> API -> FS -> IV & PM & MM & RL;
        IV -> HS & SS;
        SS -> IM;
        FS -> GW -> NW & CT;
        FS -> LS & FSs;
    }

|

----

|

.. _arch-components:

==========
Components
==========

|

.. _arch-fabric-security:

FabricSecurity (Main Class)
----------------------------

The central orchestrator that coordinates all security services.

|

.. graphviz::

    digraph FabricSecurity {
        rankdir=LR;
        size="10,6";
        
        FS [label="FabricSecurity", shape=box, style="rounded,filled", fillcolor="#764ba2", fontcolor="white"];
        
        subgraph cluster_internal {
            label="Internal Services";
            style="dashed";
            
            IV [label="IntegrityVerifier"];
            PM [label="PermissionManager"];
            MM [label="MessageManager"];
            RL [label="RateLimiter"];
        }
        
        subgraph cluster_crypto {
            label="Cryptographic Services";
            style="dashed";
            
            HS [label="HashingService"];
            SS [label="SigningService"];
            IM [label="IdentityManager"];
        }
        
        subgraph cluster_fabric {
            label="Fabric Services";
            style="dashed";
            
            GW [label="FabricGateway"];
            NW [label="FabricNetwork"];
            CT [label="FabricContract"];
        }
        
        subgraph cluster_storage {
            label="Storage Services";
            style="dashed";
            
            LS [label="LocalStorage"];
            FSs [label="FabricStorage"];
        }
        
        FS -> IV & PM & MM & RL;
        IV -> HS & SS;
        SS -> IM;
        FS -> GW -> NW & CT;
        FS -> LS & FSs;
    }

|

**Key Responsibilities:**

* Initialize and configure all security services
* Coordinate inter-service communication
* Provide unified API for security operations
* Manage lifecycle of security components

|

.. _arch-crypto:

Cryptographic Layer
------------------

|

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Component
     - Description
   * - **HashingService**
     - SHA-256 hash computation for code and message integrity
   * - **SigningService**
     - ECDSA (secp256k1) signing and verification operations
   * - **IdentityManager**
     - X.509 certificate management and identity verification

|

|

.. graphviz::

    digraph CryptoFlow {
        rankdir=LR;
        size="10,4";
        
        Input [label="Input Data", shape=ellipse, fillcolor="#E3F2FD"];
        Hash [label="SHA-256 Hash", shape=box, fillcolor="#FF9800", fontcolor="white"];
        Sign [label="ECDSA Sign", shape=box, fillcolor="#4CAF50", fontcolor="white"];
        Output [label="Digital Signature", shape=ellipse, fillcolor="#E3F2FD"];
        
        Input -> Hash -> Sign -> Output;
    }

|

----

|

.. _arch-security-services:

Security Services
-----------------

|

.. _arch-integrity:

IntegrityVerifier
^^^^^^^^^^^^^^^^^

Verifies code integrity using SHA-256 hashes stored on the Fabric ledger.

|

.. mermaid::

    flowchart LR
        A[Source Code] --> B[Compute SHA-256]
        B --> C[Sign Hash]
        C --> D[Store on Fabric]
        
        E[Runtime] --> F[Get Hash from Fabric]
        F --> G[Compare with Local]
        G --> H{Hash Match?}
        H -->|Yes| I[✓ Code Valid]
        H -->|No| J[❌ Code Tampered]

|

|

.. _arch-permissions:

PermissionManager
^^^^^^^^^^^^^^^^^

Manages communication permissions between participants.

|

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Permission Type
     - Description
   * - **BIDIRECTIONAL**
     - Full bidirectional communication
   * - **OUTBOUND**
     - Only outgoing messages allowed
   * - **INBOUND**
     - Only incoming messages allowed
   * - **NONE**
     - No communication allowed

|

|

.. _arch-messages:

MessageManager
^^^^^^^^^^^^^^

Handles secure message creation, signing, and verification.

|

.. mermaid::

    sequenceDiagram
        participant Sender
        participant MM as MessageManager
        participant SS as SigningService
        
        Sender->>MM: create_message(content, recipient)
        MM->>MM: Validate permissions
        MM->>SS: Sign payload
        SS-->>MM: Return signature
        MM-->>Sender: Return SignedMessage
        
        Sender->>MM: verify_message(message)
        MM->>MM: Check signature
        MM->>MM: Verify hash
        MM-->>Sender: Return verification result

|

|

.. _arch-rate-limiter:

RateLimiter
^^^^^^^^^^^

Implements token bucket algorithm for rate limiting.

|

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Parameter
     - Description
   * - **rate**
     - Tokens added per second
   * - **capacity**
     - Maximum token bucket size
   * - **consume**
     - Tokens consumed per request

|

----

|

.. _arch-fabric:

Fabric Integration
------------------

|

.. graphviz::

    digraph FabricIntegration {
        rankdir=TB;
        size="8,6";
        
        subgraph cluster_app {
            label="Application";
            style="rounded";
            
            FS [label="FabricSecurity", shape=box, fillcolor="#764ba2", fontcolor="white"];
        }
        
        subgraph cluster_gateway {
            label="Fabric Gateway";
            style="rounded";
            
            GW [label="FabricGateway", shape=box, fillcolor="#2196F3", fontcolor="white"];
            NW [label="FabricNetwork", shape=box, fillcolor="#2196F3", fontcolor="white"];
            CT [label="FabricContract", shape=box, fillcolor="#2196F3", fontcolor="white"];
        }
        
        subgraph cluster_ledger {
            label="Hyperledger Fabric Ledger";
            style="rounded";
            
            BC [label="Blockchain", shape=box, fillcolor="#607D8B", fontcolor="white"];
            SC [label="Smart Contracts", shape=box, fillcolor="#607D8B", fontcolor="white"];
        }
        
        FS -> GW -> NW & CT;
        NW -> BC;
        CT -> SC;
    }

|

**Gateway Connection Flow:**

|

.. mermaid::

    sequenceDiagram
        participant App as Application
        participant GW as FabricGateway
        participant NW as FabricNetwork
        participant CT as FabricContract
        participant Fabric as Hyperledger Fabric
        
        App->>GW: connect()
        GW->>NW: get_network()
        App->>CT: get_contract()
        App->>CT: submit_transaction()
        CT->>Fabric: Invoke Chaincode
        Fabric-->>CT: Transaction Result
        CT-->>App: Return Result
        App->>GW: disconnect()

|

----

|

.. _arch-storage:

Storage Layer
-------------

|

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Storage Type
     - Description
   * - **LocalStorage**
     - File-based storage with JSON serialization
   * - **FabricStorage**
     - Blockchain-based storage via chaincode

|

|

.. graphviz::

    digraph StorageLayer {
        rankdir=LR;
        size="8,4";
        
        subgraph cluster_app {
            label="Application Layer";
            FS [label="FabricSecurity"];
        }
        
        subgraph cluster_storage {
            label="Storage Abstraction";
            Abs [label="Storage Interface", shape=interface];
        }
        
        subgraph cluster_impl {
            label="Storage Implementations";
            LS [label="LocalStorage"];
            Fs [label="FabricStorage"];
        }
        
        FS -> Abs;
        Abs -> LS;
        Abs -> Fs;
    }

|

----

|

.. _arch-design-patterns:

===========
Design Patterns
===========

|

.. _arch-singleton:

Singleton Pattern
-----------------

Services use singleton pattern to ensure single instance:

|

.. code-block:: python

    class HashingService:
        _instance = None
        
        def __new__(cls):
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance

|

.. _arch-factory:

Factory Pattern
---------------

Credential creation uses factory pattern:

|

.. code-block:: python

    class IdentityFactory:
        @staticmethod
        def create_credentials(credential_type: CredentialType) -> Credentials:
            if credential_type == CredentialType.MSP:
                return MSPCredentials()
            elif credential_type == CredentialType.WALLET:
                return WalletCredentials()

|

.. _arch-strategy:

Strategy Pattern
----------------

Rate limiting strategies:

|

.. code-block:: python

    class RateLimiter:
        def __init__(self, strategy: RateLimitStrategy):
            self.strategy = strategy
        
        def should_allow(self) -> bool:
            return self.strategy.should_allow()

|

----

|

.. _arch-security-model:

=============
Security Model
=============

|

.. _arch-zero-trust:

Zero Trust Principles
----------------------

|

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Principle
     - Implementation
   * - **Verify Explicitly**
     - Every request is authenticated and authorized using cryptographic verification
   * - **Least Privilege Access**
     - Participants receive minimum necessary permissions
   * - **Assume Breach**
     - Continuous verification and monitoring

|

|

.. _arch-threat-mitigation:

Threat Mitigation
-----------------

|

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Threat
     - Mitigation Strategy
   * - **Code Tampering**
     - SHA-256 hash verification against Fabric ledger
   * - **Identity Spoofing**
     - ECDSA signature verification with X.509 certificates
   * - **Message Replay**
     - Timestamp validation and nonce usage
   * - **Man-in-the-Middle**
     - TLS transport and message signing
   * - **Denial of Service**
     - Rate limiting with token bucket algorithm

|

|

.. _arch-audit:

Audit & Compliance
------------------

All security operations generate audit logs:

|

.. code-block:: python

    class AuditLog:
        def __init__(self):
            self.entries: List[AuditEntry] = []
        
        def log(self, operation: str, participant: str, result: bool):
            self.entries.append(AuditEntry(
                timestamp=datetime.now(),
                operation=operation,
                participant=participant,
                result=result
            ))

|

----

|

.. _arch-performance:

===========
Performance
===========

|

.. _arch-caching:

Caching Strategy
----------------

Certificate caching with LRU eviction:

|

.. code-block:: python

    from functools import lru_cache
    
    class IdentityManager:
        @lru_cache(maxsize=1024, ttl=3600)
        def get_certificate(self, participant_id: str) -> Certificate:
            """Cache certificates for 1 hour with LRU eviction."""
            return self._fetch_certificate(participant_id)

|

|

.. _arch-optimization:

Optimizations
-------------

* **Batch Verification**: Multiple signatures verified in parallel
* **Connection Pooling**: Gateway connections reused
* **Lazy Loading**: Components loaded on-demand
* **Memory Pooling**: Pre-allocated buffers for crypto operations

|

----

|

.. _arch-scalability:

==========
Scalability
==========

|

wFabricSecurity supports horizontal scaling through:

|

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Strategy
     - Description
   * - **Stateless Services**
     - Security services maintain no session state
   * - **Distributed Caching**
     - Redis-compatible cache for certificates
   * **Load Balancing**
     - Multiple instances behind load balancer
   * - **Chaincode Sharding**
     - Partition data across multiple channels

|

----

|

.. _arch-deployment:

==========
Deployment
==========

|

.. graphviz::

    digraph Deployment {
        rankdir=LR;
        size="10,5";
        
        subgraph cluster_k8s {
            label="Kubernetes Cluster";
            style="rounded";
            color="#326CE5";
            
            subgraph cluster_nodes {
                label="Nodes";
                style="dashed";
                
                Pod1 [label="wFabricSecurity Pod 1", shape=box];
                Pod2 [label="wFabricSecurity Pod 2", shape=box];
                Pod3 [label="wFabricSecurity Pod 3", shape=box];
            }
            
            LB [label="Load Balancer", shape=ellipse, fillcolor="#4CAF50", fontcolor="white"];
        }
        
        subgraph cluster_fabric {
            label="Hyperledger Fabric";
            style="rounded";
            color="#333";
            
            ORG1 [label="Org1 Peer"];
            ORG2 [label="Org2 Peer"];
            ORDERER [label="Orderer"];
        }
        
        LB -> Pod1 & Pod2 & Pod3;
        Pod1 -> ORG1;
        Pod2 -> ORG2;
        Pod3 -> ORDERER;
    }

|

|

**Deployment Requirements:**

* Python 3.10+
* Hyperledger Fabric 2.x or 3.x
* Minimum 2GB RAM per instance
* Network connectivity to Fabric peers

|

----

|

.. seealso::

   * :ref:`api_reference` - Complete API documentation
   * :ref:`tutorials` - Step-by-step implementation guides
   * :ref:`getting_started` - Quick start guide
