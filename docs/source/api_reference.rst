API Reference
==============

This section provides detailed documentation for all wFabricSecurity classes and methods.

Main Classes
------------

FabricSecurity
~~~~~~~~~~~~~

The main class implementing the complete Zero Trust security system.

.. autoclass:: wFabricSecurity.fabric_security.fabric_security.FabricSecurity
   :members:
   :undoc-members:
   :show-inheritance:

FabricSecuritySimple
~~~~~~~~~~~~~~~~~~~

Simplified version of FabricSecurity for basic use cases.

.. autoclass:: wFabricSecurity.fabric_security.fabric_security.FabricSecuritySimple
   :members:
   :undoc-members:
   :show-inheritance:

Security Classes
----------------

IntegrityVerifier
~~~~~~~~~~~~~~~~

Verifies code integrity using SHA-256 hashing.

.. autoclass:: wFabricSecurity.fabric_security.security.integrity.IntegrityVerifier
   :members:
   :undoc-members:
   :show-inheritance:

PermissionManager
~~~~~~~~~~~~~~~~

Manages communication permissions between participants.

.. autoclass:: wFabricSecurity.fabric_security.security.permissions.PermissionManager
   :members:
   :undoc-members:
   :show-inheritance:

MessageManager
~~~~~~~~~~~~~

Manages message creation, verification, and expiration.

.. autoclass:: wFabricSecurity.fabric_security.security.messages.MessageManager
   :members:
   :undoc-members:
   :show-inheritance:

RateLimiter
~~~~~~~~~~~

Token bucket rate limiter for DoS protection.

.. autoclass:: wFabricSecurity.fabric_security.security.rate_limiter.RateLimiter
   :members:
   :undoc-members:
   :show-inheritance:

Cryptographic Services
---------------------

HashingService
~~~~~~~~~~~~~~

Provides SHA-256 and BLAKE2 hashing services.

.. autoclass:: wFabricSecurity.fabric_security.crypto.hashing.HashingService
   :members:
   :undoc-members:
   :show-inheritance:

SigningService
~~~~~~~~~~~~~~

ECDSA and HMAC signing services.

.. autoclass:: wFabricSecurity.fabric_security.crypto.signing.SigningService
   :members:
   :undoc-members:
   :show-inheritance:

IdentityManager
~~~~~~~~~~~~~~~

X.509 certificate management with caching.

.. autoclass:: wFabricSecurity.fabric_security.crypto.identity.IdentityManager
   :members:
   :undoc-members:
   :show-inheritance:

Fabric Classes
--------------

FabricGateway
~~~~~~~~~~~~~

Gateway for Hyperledger Fabric communication.

.. autoclass:: wFabricSecurity.fabric_security.fabric.gateway.FabricGateway
   :members:
   :undoc-members:
   :show-inheritance:

FabricContract
~~~~~~~~~~~~~~

Interface to Fabric chaincode functions.

.. autoclass:: wFabricSecurity.fabric_security.fabric.contract.FabricContract
   :members:
   :undoc-members:
   :show-inheritance:

FabricNetwork
~~~~~~~~~~~~~

Fabric network abstraction.

.. autoclass:: wFabricSecurity.fabric_security.fabric.network.FabricNetwork
   :members:
   :undoc-members:
   :show-inheritance:

Storage Classes
----------------

LocalStorage
~~~~~~~~~~~

Local JSON file storage (fallback when Fabric unavailable).

.. autoclass:: wFabricSecurity.fabric_security.storage.local.LocalStorage
   :members:
   :undoc-members:
   :show-inheritance:

FabricStorage
~~~~~~~~~~~~~

Hyperledger Fabric blockchain storage.

.. autoclass:: wFabricSecurity.fabric_security.storage.fabric_storage.FabricStorage
   :members:
   :undoc-members:
   :show-inheritance:

Data Models
-----------

Message
~~~~~~~

Represents a signed message with integrity verification.

.. autoclass:: wFabricSecurity.fabric_security.core.models.Message
   :members:
   :undoc-members:
   :show-inheritance:

Participant
~~~~~~~~~~~

Represents a participant with identity and permissions.

.. autoclass:: wFabricSecurity.fabric_security.core.models.Participant
   :members:
   :undoc-members:
   :show-inheritance:

Task
~~~~~

Represents a task with hash tracking.

.. autoclass:: wFabricSecurity.fabric_security.core.models.Task
   :members:
   :undoc-members:
   :show-inheritance:

Exceptions
----------

Security Exceptions
~~~~~~~~~~~~~~~~~~

All security-related exceptions:

.. automodule:: wFabricSecurity.fabric_security.core.exceptions
   :members:
   :undoc-members:

Enumerations
------------

CommunicationDirection
~~~~~~~~~~~~~~~~~~~~~

Direction of communication permissions.

.. autoclass:: wFabricSecurity.fabric_security.core.enums.CommunicationDirection
   :members:
   :undoc-members:
   :show-inheritance:

DataType
~~~~~~~~~

Supported data types for messages.

.. autoclass:: wFabricSecurity.fabric_security.core.enums.DataType
   :members:
   :undoc-members:
   :show-inheritance:

ParticipantStatus
~~~~~~~~~~~~~~~~~

Status of a participant.

.. autoclass:: wFabricSecurity.fabric_security.core.enums.ParticipantStatus
   :members:
   :undoc-members:
   :show-inheritance:

TaskStatus
~~~~~~~~~~~

Status of a task.

.. autoclass:: wFabricSecurity.fabric_security.core.enums.TaskStatus
   :members:
   :undoc-members:
   :show-inheritance:

VerificationLevel
~~~~~~~~~~~~~~~~~

Level of verification to perform.

.. autoclass:: wFabricSecurity.fabric_security.core.enums.VerificationLevel
   :members:
   :undoc-members:
   :show-inheritance:
