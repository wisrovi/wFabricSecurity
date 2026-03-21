.. _glossary:

########
Glossary
########

This glossary defines key terms and concepts used in wFabricSecurity and Hyperledger Fabric.

|

.. contents::
   :local:
   :depth: 3

|

----

|

.. _glossary-fundamentals:

=============
Fundamentals
=============

|

.. _glossary-zero-trust:

Zero Trust
----------

**Definition:** A security model that assumes no implicit trust and requires continuous verification of every request, regardless of its origin.

**In wFabricSecurity:** Every transaction must be cryptographically verified before processing, regardless of the participant's network location.

|

.. _glossary-identity:

Identity
--------

**Definition:** A unique representation of a participant (user, organization, or component) within the system.

**In wFabricSecurity:** Managed through X.509 certificates and MSP (Membership Service Provider) credentials.

|

.. _glossary-msp:

MSP (Membership Service Provider)
----------------------------------

**Definition:** A component that provides credentials to participants for authentication and authorization within a Fabric network.

**See Also:** :class:`wFabricSecurity.fabric_security.core.models.MSPConfig`

|

----

|

.. _glossary-cryptography:

==============
Cryptography
==============

|

.. _glossary-hashing:

Hashing
-------

**Definition:** The process of converting input data into a fixed-size string of bytes using a mathematical algorithm.

**Algorithm Used:** SHA-256 (Secure Hash Algorithm 256-bit)

**In wFabricSecurity:** Used for code integrity verification and message integrity checks.

|

.. _glossary-ecdsa:

ECDSA (Elliptic Curve Digital Signature Algorithm)
---------------------------------------------------

**Definition:** A public-key cryptographic algorithm for digital signatures using elliptic curve mathematics.

**Curve Used:** secp256k1

**In wFabricSecurity:** Used for signing and verifying messages to ensure authenticity.

|

.. _glossary-digital-signature:

Digital Signature
-----------------

**Definition:** A mathematical scheme for verifying the authenticity and integrity of digital messages or documents.

**Components:**

* Private key: Used to create the signature
* Public key: Used to verify the signature
* Hash: The digest of the message being signed

|

.. _glossary-certificate:

X.509 Certificate
------------------

**Definition:** A digital document that binds a public key to an identity, issued by a trusted Certificate Authority (CA).

**Format:** DER or PEM encoding

|

----

|

.. _glossary-security:

=============
Security
=============

|

.. _glossary-integrity:

Integrity
---------

**Definition:** The assurance that data has not been modified or tampered with during transmission or storage.

**In wFabricSecurity:** Verified using SHA-256 hash comparison against ledger-stored values.

|

.. _glossary-authenticity:

Authenticity
------------

**Definition:** The guarantee that a message or transaction genuinely originated from the claimed sender.

**In wFabricSecurity:** Verified using ECDSA signature verification.

|

.. _glossary-availability:

Availability
------------

**Definition:** The assurance that authorized users can access the system and its resources when needed.

**In wFabricSecurity:** Protected through rate limiting and retry logic.

|

.. _glossary-confidentiality:

Confidentiality
---------------

**Definition:** The assurance that information is accessible only to authorized parties.

**In wFabricSecurity:** Implemented through TLS transport and access control permissions.

|

.. _glossary-non-repudiation:

Non-Repudiation
---------------

**Definition:** The guarantee that a sender cannot deny having sent a message.

**In wFabricSecurity:** Achieved through digital signatures that bind the sender's identity to the message.

|

----

|

.. _glossary-fabric:

=============
Hyperledger Fabric
=============

|

.. _glossary-channel:

Channel
-------

**Definition:** A private subnet of communication between organizations within a Fabric network, used for private and confidential transactions.

|

.. _glossary-chaincode:

Chaincode
---------

**Definition:** Smart contracts in Hyperledger Fabric that define the business logic and state transformations.

**Also Known As:** Smart Contract

|

.. _glossary-endorsement:

Endorsement
-----------

**Definition:** The process by which participating organizations validate and sign a transaction proposal before it's committed to the ledger.

|

.. _glossary-ledger:

Ledger
------

**Definition:** The immutable record of all transactions in a Fabric network, consisting of:

* **World State:** Current state of all assets
* **Transaction Log:** Complete history of transactions

|

.. _glossary-peer:

Peer
----

**Definition:** A node in a Fabric network that hosts a copy of the ledger and runs chaincode.

|

.. _glossary-orderer:

Orderer
-------

**Definition:** A node responsible for ordering transactions into blocks and distributing them to peers.

|

----

|

.. _glossary-messages:

=============
Messages
=============

|

.. _glossary-signed-message:

SignedMessage
-------------

**Definition:** A message that has been cryptographically signed using ECDSA.

**Components:**

.. code-block:: python

    @dataclass
    class SignedMessage:
        payload: str          # Original message content
        sender: str           # Sender's identity (CN)
        recipient: str        # Recipient's identity (CN)
        signature: bytes      # ECDSA signature
        timestamp: datetime   # Creation timestamp

|

.. _glossary-communication:

CommunicationDirection
----------------------

**Definition:** Enum defining the allowed direction of communication between participants.

**Values:**

.. list-table::
   :header-rows: 1

   * - Value
     - Description
   * - ``BIDIRECTIONAL``
     - Full bidirectional communication allowed
   * - ``OUTBOUND``
     - Only outgoing messages allowed
   * - ``INBOUND``
     - Only incoming messages allowed
   * - ``NONE``
     - No communication allowed

|

----

|

.. _glossary-storage:

=============
Storage
=============

|

.. _glossary-local-storage:

LocalStorage
------------

**Definition:** File-based storage implementation using JSON serialization for local persistence.

|

.. _glossary-fabric-storage:

FabricStorage
-------------

**Definition:** Blockchain-based storage implementation that persists data through chaincode transactions.

|

----

|

.. _glossary-algorithms:

=============
Algorithms
=============

|

.. _glossary-token-bucket:

Token Bucket Algorithm
-----------------------

**Definition:** An algorithm for rate limiting that allows burst traffic while maintaining a long-term average rate.

**Parameters:**

* **rate:** Tokens added per second
* **capacity:** Maximum tokens in the bucket
* **consume:** Tokens required per request

|

.. _glossary-exponential-backoff:

Exponential Backoff
-------------------

**Definition:** A retry strategy where the wait time between retries doubles after each failed attempt.

**Formula:** ``wait_time = base_delay * 2^attempt + jitter``

|

.. _glossary-lru-cache:

LRU Cache (Least Recently Used)
-------------------------------

**Definition:** A caching algorithm that evicts the least recently accessed items when the cache reaches its capacity.

**In wFabricSecurity:** Used for certificate caching with configurable TTL.

|

----

|

.. _glossary-errors:

=========
Errors
=========

|

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Error Type
     - Description
   * - **CodeIntegrityError**
     - Code hash mismatch detected - possible tampering
   * - **SignatureVerificationError**
     - ECDSA signature verification failed
   * - **PermissionDeniedError**
     - Communication not permitted between participants
   * - **RateLimitExceededError**
     - Too many requests, rate limit exceeded
   * - **ConnectionError**
     - Unable to connect to Fabric network
   * - **CertificateError**
     - Certificate validation or parsing failed

|

|

.. seealso::

   * :ref:`api_reference` - Complete API documentation
   * :ref:`architecture` - System architecture details
   * :ref:`faq` - Frequently asked questions
