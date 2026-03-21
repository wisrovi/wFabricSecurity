.. _api_reference:

=============
API Reference
=============

Complete documentation for all wFabricSecurity classes, methods, and functions.

|

.. contents::
   :local:
   :depth: 3

|

----

|

.. _api-main-classes:

============
Main Classes
============

|

.. _api-fabric-security:

FabricSecurity
-------------

|

.. sidebar:: Quick Reference

   **Import:** ``from wFabricSecurity import FabricSecurity``

   **Instantiation:**

   .. code-block:: python

      security = FabricSecurity(
          me="ParticipantName",
          msp_path="/path/to/msp",
          gateway_path="/path/to/gateway"
      )

|

The main class implementing the complete Zero Trust security system for Hyperledger Fabric.

|

.. autoclass:: wFabricSecurity.fabric_security.fabric_security.FabricSecurity
   :members:
   :undoc-members:
   :show-inheritance:

|

**Example Usage:**

|

.. code-block:: python

   from wFabricSecurity import FabricSecurity

   # Initialize security system
   security = FabricSecurity(
       me="Master",
       msp_path="/path/to/msp",
       gateway_path="/path/to/gateway"
   )

   # Register identity
   security.register_identity()

   # Register code integrity
   security.register_code(["master.py", "utils.py"], "1.0.0")

   # Register communication permissions
   security.register_communication("CN=Master", "CN=Slave")

   # Create and send signed message
   message = security.create_message(
       recipient="CN=Slave",
       content='{"operation": "process"}'
   )

   # Verify incoming message
   if security.verify_message(message):
       print("Message verified successfully!")

|

|

.. _api-fabric-security-simple:

FabricSecuritySimple
--------------------

|

.. sidebar:: Quick Reference

   **Import:** ``from wFabricSecurity import FabricSecuritySimple``

   **Instantiation:**

   .. code-block:: python

      security = FabricSecuritySimple(msp_path="/path/to/msp")

|

Simplified version of FabricSecurity for basic use cases.

|

.. autoclass:: wFabricSecurity.fabric_security.fabric_security.FabricSecuritySimple
   :members:
   :undoc-members:
   :show-inheritance:

|

**Example Usage:**

|

.. code-block:: python

   from wFabricSecurity import FabricSecuritySimple

   # Simplified initialization
   security = FabricSecuritySimple(msp_path="/path/to/msp")

   # One-line verification
   result = security.verify_and_process(
       payload={"action": "update"},
       sender="CN=Master"
   )

|

----

|

.. _api-security-services:

=================
Security Services
=================

|

.. _api-integrity-verifier:

IntegrityVerifier
----------------

|

.. sidebar:: Quick Reference

   **Import:** ``from wFabricSecurity.fabric_security.security.integrity import IntegrityVerifier``

   **Purpose:** SHA-256 hash verification of source code

|

Verifies code integrity using SHA-256 hashing.

|

.. autoclass:: wFabricSecurity.fabric_security.security.integrity.IntegrityVerifier
   :members:
   :undoc-members:
   :show-inheritance:

|

**Workflow:**

|

.. graphviz::

    digraph IntegrityFlow {
        rankdir=LR;
        size="8,4";
        
        Code [label="Source Code", shape=ellipse, fillcolor="#E3F2FD"];
        Hash [label="Compute SHA-256", shape=box, fillcolor="#FF9800", fontcolor="white"];
        Store [label="Store Hash", shape=box, fillcolor="#4CAF50", fontcolor="white"];
        
        Runtime [label="Runtime", shape=ellipse, fillcolor="#FFEBEE"];
        Compare [label="Compare Hashes", shape=box, fillcolor="#9C27B0", fontcolor="white"];
        Result [label="Valid/Invalid", shape=ellipse];
        
        Code -> Hash -> Store;
        Runtime -> Compare;
        Store -> Compare;
        Compare -> Result;
    }

|

|

.. _api-permission-manager:

PermissionManager
-----------------

|

.. sidebar:: Quick Reference

   **Import:** ``from wFabricSecurity.fabric_security.security.permissions import PermissionManager``

   **Purpose:** Manage communication permissions between participants

|

Manages communication permissions between participants.

|

.. autoclass:: wFabricSecurity.fabric_security.security.permissions.PermissionManager
   :members:
   :undoc-members:
   :show-inheritance:

|

**Permission Types:**

|

.. list-table::
   :header-rows: 1

   * - Direction
     - Description
     - Use Case
   * - ``BIDIRECTIONAL``
     - Full communication allowed
     - Peer-to-peer messaging
   * - ``OUTBOUND``
     - Only sending allowed
     - Publisher/subscriber
   * - ``INBOUND``
     - Only receiving allowed
     - Subscriber-only node
   * - ``NONE``
     - No communication
     - Isolated verification

|

|

.. _api-message-manager:

MessageManager
-------------

|

.. sidebar:: Quick Reference

   **Import:** ``from wFabricSecurity.fabric_security.security.messages import MessageManager``

   **Purpose:** Create and verify signed messages

|

Manages message creation, verification, and expiration.

|

.. autoclass:: wFabricSecurity.fabric_security.security.messages.MessageManager
   :members:
   :undoc-members:
   :show-inheritance:

|

**Message Flow:**

|

.. mermaid::

    sequenceDiagram
        participant Sender
        participant MM as MessageManager
        participant SS as SigningService
        participant Verifier
        
        Sender->>MM: create_message(content, recipient)
        MM->>SS: sign(payload)
        SS-->>MM: signature
        MM-->>Sender: SignedMessage
        
        Sender->>Verifier: verify_message(SignedMessage)
        Verifier->>MM: validate(message)
        MM->>MM: check_signature()
        MM->>MM: check_permissions()
        MM->>MM: check_expiration()
        MM-->>Verifier: VerificationResult
        Verifier-->>Sender: True/False

|

|

.. _api-rate-limiter:

RateLimiter
-----------

|

.. sidebar:: Quick Reference

   **Import:** ``from wFabricSecurity.fabric_security.security.rate_limiter import RateLimiter``

   **Purpose:** Token bucket rate limiting

|

Token bucket rate limiter for DoS protection.

|

.. autoclass:: wFabricSecurity.fabric_security.security.rate_limiter.RateLimiter
   :members:
   :undoc-members:
   :show-inheritance:

|

**Algorithm Visualization:**

|

.. graphviz::

    digraph TokenBucket {
        rankdir=TB;
        size="6,6";
        
        subgraph cluster_bucket {
            label="Token Bucket";
            style="rounded";
            
            subgraph tokens {
                rank=same;
                T1 [label="●", shape=circle, fillcolor="#4CAF50"];
                T2 [label="●", shape=circle, fillcolor="#4CAF50"];
                T3 [label="●", shape=circle, fillcolor="#4CAF50"];
                T4 [label="○", shape=circle, fillcolor="#E0E0E0"];
            }
            
            rate [label="rate: 2/sec", shape=note];
            capacity [label="capacity: 5", shape=note];
        }
        
        request [label="Request", shape=ellipse, fillcolor="#E3F2FD"];
        check [label="Has Token?", shape=diamond, fillcolor="#FF9800", fontcolor="white"];
        allow [label="✓ Allow", shape=box, fillcolor="#4CAF50", fontcolor="white"];
        deny [label="✗ Deny", shape=box, fillcolor="#F44336", fontcolor="white"];
        
        request -> check;
        check -> allow [label="Yes"];
        check -> deny [label="No"];
    }

|

|

.. _api-retry-logic:

RetryLogic
---------

|

.. sidebar:: Quick Reference

   **Import:** ``from wFabricSecurity.fabric_security.security.retry import RetryLogic``

   **Purpose:** Exponential backoff with jitter

|

Exponential backoff retry logic.

|

.. autoclass:: wFabricSecurity.fabric_security.security.retry.RetryLogic
   :members:
   :undoc-members:
   :show-inheritance:

|

**Backoff Schedule:**

|

.. code-block:: text

   Attempt 1: wait = 1.0s (base_delay)
   Attempt 2: wait = 2.0s (base_delay * 2^1)
   Attempt 3: wait = 4.0s (base_delay * 2^2)
   Attempt 4: wait = 8.0s (base_delay * 2^3)
   Attempt 5: wait = 16.0s (base_delay * 2^4)
   
   + jitter: random(0, wait * jitter_factor)

|

----

|

.. _api-crypto-services:

====================
Cryptographic Services
====================

|

.. _api-hashing-service:

HashingService
-------------

|

.. sidebar:: Quick Reference

   **Import:** ``from wFabricSecurity.fabric_security.crypto.hashing import HashingService``

   **Algorithms:** SHA-256, BLAKE2

|

Provides SHA-256 and BLAKE2 hashing services.

|

.. autoclass:: wFabricSecurity.fabric_security.crypto.hashing.HashingService
   :members:
   :undoc-members:
   :show-inheritance:

|

**Usage Example:**

|

.. code-block:: python

   from wFabricSecurity.fabric_security.crypto.hashing import HashingService

   hasher = HashingService()

   # Hash a file
   file_hash = hasher.hash_file("path/to/file.py")

   # Hash a string
   data_hash = hasher.hash_bytes(b"Hello, World!")

   # Verify
   is_valid = hasher.verify_hash(data_hash, expected_hash)

|

|

.. _api-signing-service:

SigningService
-------------

|

.. sidebar:: Quick Reference

   **Import:** ``from wFabricSecurity.fabric_security.crypto.signing import SigningService``

   **Algorithm:** ECDSA (secp256k1)

|

ECDSA and HMAC signing services.

|

.. autoclass:: wFabricSecurity.fabric_security.crypto.signing.SigningService
   :members:
   :undoc-members:
   :show-inheritance:

|

**Signing Flow:**

|

.. graphviz::

    digraph SigningFlow {
        rankdir=LR;
        size="8,4";
        
        Message [label="Message", shape=ellipse, fillcolor="#E3F2FD"];
        Hash [label="Hash (SHA-256)", shape=box, fillcolor="#FF9800", fontcolor="white"];
        Sign [label="ECDSA Sign", shape=box, fillcolor="#4CAF50", fontcolor="white"];
        Signature [label="Digital Signature", shape=ellipse, fillcolor="#E8F5E9"];
        
        Private [label="Private Key", shape=box, fillcolor="#F44336", fontcolor="white"];
        Public [label="Public Key", shape=box, fillcolor="#2196F3", fontcolor="white"];
        
        Message -> Hash;
        Hash -> Sign;
        Private -> Sign;
        Sign -> Signature;
        Sign -> Public;
    }

|

|

.. _api-identity-manager:

IdentityManager
--------------

|

.. sidebar:: Quick Reference

   **Import:** ``from wFabricSecurity.fabric_security.crypto.identity import IdentityManager``

   **Features:** X.509 certificates, MSP, caching

|

X.509 certificate management with caching.

|

.. autoclass:: wFabricSecurity.fabric_security.crypto.identity.IdentityManager
   :members:
   :undoc-members:
   :show-inheritance:

|

**Certificate Caching:**

|

.. code-block:: python

   from wFabricSecurity.fabric_security.crypto.identity import IdentityManager

   identity = IdentityManager(cache_size=1024, ttl=3600)

   # First call - fetches from disk
   cert = identity.get_certificate("CN=Master")

   # Subsequent calls - served from cache
   cert = identity.get_certificate("CN=Master")

|

----

|

.. _api-fabric-classes:

=================
Fabric Classes
=================

|

.. _api-fabric-gateway:

FabricGateway
------------

|

.. sidebar:: Quick Reference

   **Import:** ``from wFabricSecurity.fabric_security.fabric.gateway import FabricGateway``

   **Purpose:** Connect to Hyperledger Fabric network

|

Gateway for Hyperledger Fabric communication.

|

.. autoclass:: wFabricSecurity.fabric_security.fabric.gateway.FabricGateway
   :members:
   :undoc-members:
   :show-inheritance:

|

**Connection Diagram:**

|

.. graphviz::

    digraph GatewayConnection {
        rankdir=TB;
        size="8,5";
        
        App [label="Application", shape=box, fillcolor="#667eea", fontcolor="white"];
        GW [label="FabricGateway", shape=box, fillcolor="#764ba2", fontcolor="white"];
        
        subgraph cluster_fabric {
            label="Hyperledger Fabric Network";
            style="rounded";
            
            NW [label="FabricNetwork", shape=box, fillcolor="#2196F3", fontcolor="white"];
            CT [label="FabricContract", shape=box, fillcolor="#2196F3", fontcolor="white"];
            Peer [label="Peer 1", shape=box, fillcolor="#607D8B", fontcolor="white"];
            Orderer [label="Orderer", shape=box, fillcolor="#607D8B", fontcolor="white"];
        }
        
        App -> GW;
        GW -> NW;
        GW -> CT;
        NW -> Peer;
        CT -> Peer;
        Peer -> Orderer;
    }

|

|

.. _api-fabric-contract:

FabricContract
--------------

|

.. sidebar:: Quick Reference

   **Import:** ``from wFabricSecurity.fabric_security.fabric.contract import FabricContract``

   **Purpose:** Interact with chaincode

|

Interface to Fabric chaincode functions.

|

.. autoclass:: wFabricSecurity.fabric_security.fabric.contract.FabricContract
   :members:
   :undoc-members:
   :show-inheritance:

|

|

.. _api-fabric-network:

FabricNetwork
------------

|

.. sidebar:: Quick Reference

   **Import:** ``from wFabricSecurity.fabric_security.fabric.network import FabricNetwork``

   **Purpose:** Manage network access

|

Fabric network abstraction.

|

.. autoclass:: wFabricSecurity.fabric_security.fabric.network.FabricNetwork
   :members:
   :undoc-members:
   :show-inheritance:

|

----

|

.. _api-storage-classes:

================
Storage Classes
================

|

.. _api-local-storage:

LocalStorage
------------

|

.. sidebar:: Quick Reference

   **Import:** ``from wFabricSecurity.fabric_security.storage.local import LocalStorage``

   **Purpose:** File-based JSON storage

|

Local JSON file storage (fallback when Fabric unavailable).

|

.. autoclass:: wFabricSecurity.fabric_security.storage.local.LocalStorage
   :members:
   :undoc-members:
   :show-inheritance:

|

|

.. _api-fabric-storage:

FabricStorage
------------

|

.. sidebar:: Quick Reference

   **Import:** ``from wFabricSecurity.fabric_security.storage.fabric_storage import FabricStorage``

   **Purpose:** Blockchain-based storage

|

Hyperledger Fabric blockchain storage.

|

.. autoclass:: wFabricSecurity.fabric_security.storage.fabric_storage.FabricStorage
   :members:
   :undoc-members:
   :show-inheritance:

|

**Storage Comparison:**

|

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Feature
     - LocalStorage
     - FabricStorage
   * - **Persistence**
     - File system
     - Blockchain ledger
   * - **Consistency**
     - Eventual
     - Strong
   * - **Latency**
     - Low
     - Higher
   * - **Cost**
     - Free
     - Transaction fees
   * - **Use Case**
     - Development/DevOps
     - Production

|

----

|

.. _api-data-models:

===========
Data Models
===========

|

.. _api-message:

Message
-------

|

.. autoclass:: wFabricSecurity.fabric_security.core.models.Message
   :members:
   :undoc-members:
   :show-inheritance:

|

**JSON Serialization:**

|

.. code-block:: python

   message = Message(
       payload="Hello",
       sender="CN=Master",
       recipient="CN=Slave",
       signature=b"...",
       timestamp=datetime.now()
   )

   # Convert to dict
   data = asdict(message)

   # Convert to JSON
   json_str = json.dumps(data)

|

|

.. _api-participant:

Participant
----------

|

.. autoclass:: wFabricSecurity.fabric_security.core.models.Participant
   :members:
   :undoc-members:
   :show-inheritance:

|

|

.. _api-task:

Task
----

|

.. autoclass:: wFabricSecurity.fabric_security.core.models.Task
   :members:
   :undoc-members:
   :show-inheritance:

|

----

|

.. _api-exceptions:

==========
Exceptions
==========

|

.. automodule:: wFabricSecurity.fabric_security.core.exceptions
   :members:
   :undoc-members:

|

**Exception Hierarchy:**

|

.. graphviz::

    digraph ExceptionHierarchy {
        rankdir=BT;
        size="8,6";
        
        Exception [label="Exception", shape=box", fillcolor="#F44336", fontcolor="white"];
        
        WFabricSecurityError [label="wFabricSecurityError", shape=box", fillcolor="#FF9800", fontcolor="white"];
        CodeIntegrityError [label="CodeIntegrityError", shape=box", fillcolor="#FFEBEE"];
        SignatureVerificationError [label="SignatureVerificationError", shape=box", fillcolor="#FFEBEE"];
        PermissionDeniedError [label="PermissionDeniedError", shape=box", fillcolor="#FFEBEE"];
        RateLimitExceededError [label="RateLimitExceededError", shape=box", fillcolor="#FFEBEE"];
        ConnectionError [label="ConnectionError", shape=box", fillcolor="#FFEBEE"];
        CertificateError [label="CertificateError", shape=box", fillcolor="#FFEBEE"];
        
        Exception -> WFabricSecurityError;
        WFabricSecurityError -> CodeIntegrityError & SignatureVerificationError & PermissionDeniedError & RateLimitExceededError & ConnectionError & CertificateError;
    }

|

----

|

.. _api-enums:

==========
Enumerations
==========

|

.. _api-communication-direction:

CommunicationDirection
---------------------

Direction of communication permissions.

|

.. autoclass:: wFabricSecurity.fabric_security.core.enums.CommunicationDirection
   :members:
   :undoc-members:
   :show-inheritance:

|

|

.. _api-data-type:

DataType
--------

Supported data types for messages.

|

.. autoclass:: wFabricSecurity.fabric_security.core.enums.DataType
   :members:
   :undoc-members:
   :show-inheritance:

|

|

.. _api-participant-status:

ParticipantStatus
-----------------

Status of a participant.

|

.. autoclass:: wFabricSecurity.fabric_security.core.enums.ParticipantStatus
   :members:
   :undoc-members:
   :show-inheritance:

|

|

.. _api-task-status:

TaskStatus
----------

Status of a task.

|

.. autoclass:: wFabricSecurity.fabric_security.core.enums.TaskStatus
   :members:
   :undoc-members:
   :show-inheritance:

|

|

.. _api-verification-level:

VerificationLevel
----------------

Level of verification to perform.

|

.. autoclass:: wFabricSecurity.fabric_security.core.enums.VerificationLevel
   :members:
   :undoc-members:
   :show-inheritance:

|

|

.. seealso::

   * :ref:`tutorials` - Step-by-step implementation guides
   * :ref:`getting_started` - Quick start guide
   * :ref:`architecture` - System architecture details
