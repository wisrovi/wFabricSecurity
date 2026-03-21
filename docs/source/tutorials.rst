.. _tutorials:

=========
Tutorials
=========

Step-by-step guides for implementing wFabricSecurity in your projects.

|

.. contents::
   :local:
   :depth: 3

|

----

|

.. _tutorial-prerequisites:

============
Prerequisites
============

|

Before starting these tutorials, ensure you have:

|

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Requirement
     - Description
   * - **Python**
     - Version 3.10 or higher
   * - **pip**
     - Latest version recommended
   * - **Hyperledger Fabric**
     - Version 2.x or 3.x (for Fabric integration tutorials)
   * - **MSP Directory**
     - Path to your organization's MSP credentials
   * - **Gateway Profile**
     - Path to your Fabric gateway connection profile

|

|

.. code-block:: bash

   # Check Python version
   python --version
   
   # Check pip version
   pip --version
   
   # Install wFabricSecurity
   pip install wFabricSecurity

|

----

|

.. _tutorial-basic-setup:

==============
Tutorial 1: Basic Setup
==============

Learn how to set up wFabricSecurity for simple security operations.

|

.. dropdown:: 📚 Objectives

   * Install wFabricSecurity
   * Initialize the security system
   * Register identities
   * Create and verify messages

|

**Step 1: Installation**

|

.. code-block:: bash

   pip install wFabricSecurity

|

**Step 2: Basic Initialization**

|

Create a new file ``basic_security.py``:

|

.. code-block:: python

   from wFabricSecurity import FabricSecuritySimple

   # Initialize with MSP path
   security = FabricSecuritySimple(
       msp_path="/path/to/your/msp"
   )

   print("Security system initialized!")

|

**Step 3: Verify a Message**

|

.. code-block:: python

   from wFabricSecurity import FabricSecuritySimple

   security = FabricSecuritySimple(msp_path="/path/to/msp")

   # Incoming message
   incoming_message = {
       "payload": '{"action": "process"}',
       "sender": "CN=Master",
       "signature": b"..."  # Actual signature bytes
   }

   # Verify the message
   result = security.verify_and_process(
       payload=incoming_message["payload"],
       sender=incoming_message["sender"]
   )

   if result:
       print("✓ Message verified successfully!")
   else:
       print("✗ Verification failed!")

|

|

.. dropdown:: 📊 Expected Output

   .. code-block:: text

      Security system initialized!
      ✓ Message verified successfully!

|

|

.. dropdown:: ✅ Complete Code

   .. code-block:: python

      from wFabricSecurity import FabricSecuritySimple

      def main():
          # Initialize
          security = FabricSecuritySimple(msp_path="/path/to/msp")

          # Verify message
          result = security.verify_and_process(
              payload='{"action": "process"}',
              sender="CN=Master"
          )

          print(f"Verification: {'✓ Success' if result else '✗ Failed'}")

      if __name__ == "__main__":
          main()

|

----

|

.. _tutorial-identity-management:

====================
Tutorial 2: Identity Management
====================

Managing identities and certificates in wFabricSecurity.

|

.. dropdown:: 📚 Objectives

   * Understand X.509 certificates
   * Register participant identities
   * Manage certificate caching
   * Verify identity credentials

|

**Step 1: Understanding MSP Configuration**

|

The MSP (Membership Service Provider) contains:

|

.. code-block:: text

   msp/
   ├── cacerts/           # CA certificates
   ├── signcerts/         # Signing certificates
   ├── keystore/          # Private keys
   └── tlscacerts/        # TLS CA certificates

|

**Step 2: Register Participant Identity**

|

.. code-block:: python

   from wFabricSecurity import FabricSecurity

   # Full initialization
   security = FabricSecurity(
       me="Master",
       msp_path="/path/to/msp",
       gateway_path="/path/to/gateway"
   )

   # Register your identity
   security.register_identity()

   print(f"Identity registered: {security.me}")

|

**Step 3: Manage Multiple Participants**

|

.. code-block:: python

   from wFabricSecurity import FabricSecurity
   from wFabricSecurity.fabric_security.core.models import Participant
   from wFabricSecurity.fabric_security.core.enums import ParticipantStatus

   security = FabricSecurity(
       me="Master",
       msp_path="/path/to/msp"
   )

   # Register participants
   participants = [
       Participant(
           id="slave-1",
           common_name="CN=Slave1",
           msp_id="Org1MSP",
           status=ParticipantStatus.ACTIVE
       ),
       Participant(
           id="slave-2", 
           common_name="CN=Slave2",
           msp_id="Org1MSP",
           status=ParticipantStatus.ACTIVE
       )
   ]

   # Register in system
   for participant in participants:
       security.register_participant(participant)

   print(f"Registered {len(participants)} participants")

|

**Step 4: Certificate Caching**

|

.. code-block:: python

   from wFabricSecurity.fabric_security.crypto.identity import IdentityManager

   # Initialize with caching
   identity = IdentityManager(
       cache_size=1024,  # Max cached certificates
       ttl=3600          # 1 hour TTL
   )

   # First call - fetches from disk
   cert1 = identity.get_certificate("CN=Master")
   print("Certificate loaded from disk")

   # Second call - from cache
   cert2 = identity.get_certificate("CN=Master")
   print("Certificate served from cache")

   # Check cache stats
   stats = identity.get_cache_stats()
   print(f"Cache hits: {stats['hits']}")
   print(f"Cache misses: {stats['misses']}")

|

|

.. dropdown:: ✅ Complete Code

   .. code-block:: python

      from wFabricSecurity import FabricSecurity
      from wFabricSecurity.fabric_security.core.models import Participant
      from wFabricSecurity.fabric_security.core.enums import ParticipantStatus

      def setup_identity_system():
          # Initialize
          security = FabricSecurity(
              me="Master",
              msp_path="/path/to/msp"
          )

          # Register master identity
          security.register_identity()

          # Register other participants
          participants = [
              Participant(
                  id="slave-1",
                  common_name="CN=Slave1",
                  msp_id="Org1MSP",
                  status=ParticipantStatus.ACTIVE
              )
          ]

          for participant in participants:
              security.register_participant(participant)

          return security

      if __name__ == "__main__":
          security = setup_identity_system()
          print("Identity system configured!")

|

----

|

.. _tutorial-code-integrity:

===================
Tutorial 3: Code Integrity
===================

Implementing SHA-256 code integrity verification.

|

.. dropdown:: 📚 Objectives

   * Compute file hashes
   * Register code integrity
   * Verify code integrity at runtime
   * Handle tampering detection

|

**Step 1: Compute Code Hash**

|

.. code-block:: python

   from wFabricSecurity.fabric_security.crypto.hashing import HashingService

   hasher = HashingService()

   # Hash a single file
   file_hash = hasher.hash_file("path/to/your/code.py")
   print(f"File hash: {file_hash}")

   # Hash multiple files
   files = ["main.py", "utils.py", "models.py"]
   combined_hash = hasher.hash_files(files)
   print(f"Combined hash: {combined_hash}")

|

**Step 2: Register Code Integrity**

|

.. code-block:: python

   from wFabricSecurity import FabricSecurity

   security = FabricSecurity(
       me="Master",
       msp_path="/path/to/msp"
   )

   # Register source code files
   security.register_code(
       files=["master.py", "utils.py"],
       version="1.0.0"
   )

   print("Code integrity registered!")

|

**Step 3: Verify Code Integrity**

|

.. code-block:: python

   from wFabricSecurity import FabricSecurity
   from wFabricSecurity.fabric_security.core.exceptions import CodeIntegrityError

   security = FabricSecurity(
       me="Master",
       msp_path="/path/to/msp"
   )

   try:
       # Verify current code
       security.verify_code_integrity()
       print("✓ Code integrity verified!")

   except CodeIntegrityError as e:
       print(f"✗ Code tampering detected: {e}")

|

**Step 4: Store Hash on Fabric Ledger**

|

.. code-block:: python

   from wFabricSecurity import FabricSecurity

   security = FabricSecurity(
       me="Master",
       msp_path="/path/to/msp",
       gateway_path="/path/to/gateway"
   )

   # Register and store on ledger
   security.register_code(
       files=["secure_module.py"],
       version="1.0.0",
       store_on_ledger=True  # Store hash on Fabric
   )

   print("Code hash stored on Fabric ledger!")

|

|

.. dropdown:: 📊 Expected Output

   .. code-block:: text

      File hash: a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e
      Combined hash: 7f83b1657ff1fc53b92dc18148a1d65d
      ✓ Code integrity verified!

|

|

.. dropdown:: ✅ Complete Code

   .. code-block:: python

      from wFabricSecurity import FabricSecurity
      from wFabricSecurity.fabric_security.core.exceptions import CodeIntegrityError

      def verify_application_integrity():
          security = FabricSecurity(
              me="Master",
              msp_path="/path/to/msp"
          )

          # Register code
          security.register_code(
              files=["main.py", "utils.py"],
              version="1.0.0"
          )

          # Verify
          try:
              security.verify_code_integrity()
              return True, "Code integrity verified"
          except CodeIntegrityError as e:
              return False, f"Tampering detected: {e}"

      if __name__ == "__main__":
          success, message = verify_application_integrity()
          print(f"{'✓' if success else '✗'} {message}")

|

----

|

.. _tutorial-communication-permissions:

==========================
Tutorial 4: Communication Permissions
==========================

Setting up fine-grained communication permissions between participants.

|

.. dropdown:: 📚 Objectives

   * Define permission types
   * Register communication rules
   * Check permission status
   * Handle permission denied scenarios

|

**Step 1: Understanding Permission Types**

|

.. code-block:: python

   from wFabricSecurity.fabric_security.core.enums import CommunicationDirection

   # Available permission types
   print(f"BIDIRECTIONAL: {CommunicationDirection.BIDIRECTIONAL}")
   print(f"OUTBOUND: {CommunicationDirection.OUTBOUND}")
   print(f"INBOUND: {CommunicationDirection.INBOUND}")
   print(f"NONE: {CommunicationDirection.NONE}")

|

**Step 2: Register Communication Permissions**

|

.. code-block:: python

   from wFabricSecurity import FabricSecurity
   from wFabricSecurity.fabric_security.core.enums import CommunicationDirection

   security = FabricSecurity(
       me="Master",
       msp_path="/path/to/msp"
   )

   # Register bidirectional communication (full peer-to-peer)
   security.register_communication(
       from_participant="CN=Master",
       to_participant="CN=Slave",
       direction=CommunicationDirection.BIDIRECTIONAL
   )

   # Register outbound-only (Master can send to Analytics)
   security.register_communication(
       from_participant="CN=Master",
       to_participant="CN=Analytics",
       direction=CommunicationDirection.OUTBOUND
   )

   # Register inbound-only (Analytics receives from others)
   security.register_communication(
       from_participant="CN=Sensor",
       to_participant="CN=Analytics",
       direction=CommunicationDirection.INBOUND
   )

   print("Communication permissions configured!")

|

**Step 3: Check and Enforce Permissions**

|

.. code-block:: python

   from wFabricSecurity import FabricSecurity
   from wFabricSecurity.fabric_security.core.exceptions import PermissionDeniedError

   security = FabricSecurity(
       me="Master",
       msp_path="/path/to/msp"
   )

   # Register permissions
   security.register_communication("CN=Master", "CN=Slave")

   # Check if communication is allowed
   if security.check_permission("CN=Master", "CN=Slave"):
       print("✓ Communication allowed")
   else:
       print("✗ Communication denied")

   # Try to send message (will raise if denied)
   try:
       security.send_message(
           to="CN=Slave",
           content="Hello, Slave!"
       )
       print("✓ Message sent successfully")
   except PermissionDeniedError:
       print("✗ Permission denied - cannot send to this recipient")

|

**Step 4: Permission Matrix**

|

.. code-block:: python

   from wFabricSecurity import FabricSecurity
   from wFabricSecurity.fabric_security.core.enums import CommunicationDirection

   security = FabricSecurity(me="Master", msp_path="/path/to/msp")

   # Define organization permissions
   permissions = [
       ("CN=Master", "CN=Slave1", CommunicationDirection.BIDIRECTIONAL),
       ("CN=Master", "CN=Slave2", CommunicationDirection.BIDIRECTIONAL),
       ("CN=Master", "CN=Analytics", CommunicationDirection.OUTBOUND),
       ("CN=Sensor1", "CN=Master", CommunicationDirection.INBOUND),
   ]

   # Register all permissions
   for from_cn, to_cn, direction in permissions:
       security.register_communication(from_cn, to_cn, direction)

   # Get permission matrix
   matrix = security.get_permission_matrix()
   print("Permission Matrix:")
   for row in matrix:
       print(f"  {row['from']} -> {row['to']}: {row['direction']}")

|

|

.. dropdown:: ✅ Complete Code

   .. code-block:: python

      from wFabricSecurity import FabricSecurity
      from wFabricSecurity.fabric_security.core.enums import CommunicationDirection
      from wFabricSecurity.fabric_security.core.exceptions import PermissionDeniedError

      def setup_permissions():
          security = FabricSecurity(me="Master", msp_path="/path/to/msp")

          # Configure permissions
          security.register_communication(
              "CN=Master", "CN=Slave",
              CommunicationDirection.BIDIRECTIONAL
          )

          # Test permission
          allowed = security.check_permission("CN=Master", "CN=Slave")
          return allowed

      if __name__ == "__main__":
          result = setup_permissions()
          print(f"Permission check: {'✓ Allowed' if result else '✗ Denied'}")

|

----

|

.. _tutorial-rate-limiting:

=================
Tutorial 5: Rate Limiting
=================

Implementing rate limiting to protect against DoS attacks.

|

.. dropdown:: 📚 Objectives

   * Configure rate limiter
   * Implement token bucket algorithm
   * Handle rate limit exceeded
   * Configure per-participant limits

|

**Step 1: Basic Rate Limiting**

|

.. code-block:: python

   from wFabricSecurity.fabric_security.security.rate_limiter import RateLimiter

   # Initialize rate limiter
   limiter = RateLimiter(
       rate=10,        # 10 tokens per second
       capacity=50,    # Max 50 tokens (burst capacity)
       participant="CN=Master"
   )

   # Check if request is allowed
   for i in range(55):
       if limiter.should_allow():
           print(f"Request {i+1}: ✓ Allowed")
       else:
           print(f"Request {i+1}: ✗ Rate limited")

|

**Step 2: Integration with Security System**

|

.. code-block:: python

   from wFabricSecurity import FabricSecurity
   from wFabricSecurity.fabric_security.core.exceptions import RateLimitExceededError

   security = FabricSecurity(
       me="Master",
       msp_path="/path/to/msp",
       rate_limit=10,      # 10 requests/second
       rate_capacity=50    # Burst capacity
   )

   # Process request with rate limiting
   def process_request(request_data: dict, sender: str):
       # Check rate limit
       if not security.check_rate_limit(sender):
           raise RateLimitExceededError(f"Rate limit exceeded for {sender}")

       # Process the request
       return {"status": "success", "data": request_data}

   # Test with multiple requests
   for i in range(5):
       try:
           result = process_request(
               {"id": i, "action": "process"},
               sender="CN=Slave"
           )
           print(f"✓ Request {i+1}: {result['status']}")
       except RateLimitExceededError as e:
           print(f"✗ Request {i+1}: {e}")

|

**Step 3: Per-Participant Rate Limits**

|

.. code-block:: python

   from wFabricSecurity import FabricSecurity

   security = FabricSecurity(me="Master", msp_path="/path/to/msp")

   # Configure different limits per participant type
   rate_configs = {
       "CN=Master": {"rate": 100, "capacity": 500},      # High priority
       "CN=Slave": {"rate": 50, "capacity": 200},      # Normal priority
       "CN=Sensor": {"rate": 10, "capacity": 50},      # IoT devices
   }

   for participant, config in rate_configs.items():
       security.configure_rate_limit(
           participant=participant,
           rate=config["rate"],
           capacity=config["capacity"]
       )

   print("Rate limits configured per participant!")

|

|

.. dropdown:: 📊 Token Bucket Visualization

   .. code-block:: text

      Time ->
      Token Bucket State:
      
      t=0s: [●●●●●] 5/50 tokens
      t=1s: [●●●●●●●] 7/50 tokens (added 2)
      t=2s: [●●●●●●●●●] 9/50 tokens
      ...
      t=25s: [●●●●●●●●●●●●●●●] 50/50 tokens (full)
      
      Burst: Up to 50 requests can be made at once

|

|

.. dropdown:: ✅ Complete Code

   .. code-block:: python

      from wFabricSecurity import FabricSecurity
      from wFabricSecurity.fabric_security.core.exceptions import RateLimitExceededError

      def secure_request_handler(request_data: dict, sender: str):
          security = FabricSecurity(
              me="Master",
              msp_path="/path/to/msp",
              rate_limit=10,
              rate_capacity=50
          )

          if not security.check_rate_limit(sender):
              raise RateLimitExceededError(f"Rate limit exceeded: {sender}")

          return {"status": "processed", "sender": sender}

      if __name__ == "__main__":
          for i in range(3):
              try:
                  result = secure_request_handler(
                      {"id": i},
                      sender="CN=Master"
                  )
                  print(f"✓ Request {i+1}: {result['status']}")
              except RateLimitExceededError as e:
                  print(f"✗ Rate limited: {e}")

|

----

|

.. _tutorial-fabric-integration:

======================
Tutorial 6: Fabric Integration
======================

Connecting wFabricSecurity to a Hyperledger Fabric network.

|

.. dropdown:: 📚 Objectives

   * Connect to Fabric gateway
   * Interact with chaincode
   * Store data on Fabric ledger
   * Query ledger data

|

**Step 1: Gateway Connection Setup**

|

.. code-block:: python

   from wFabricSecurity.fabric_security.fabric.gateway import FabricGateway

   # Initialize gateway
   gateway = FabricGateway(
       gateway_path="/path/to/connection-profile.yaml",
       identity="Admin@org1.example.com",
       msp_path="/path/to/msp"
   )

   # Connect
   gateway.connect()

   print("Connected to Fabric network!")

   # Don't forget to disconnect when done
   # gateway.disconnect()

|

**Step 2: Access Network and Contract**

|

.. code-block:: python

   from wFabricSecurity import FabricSecurity

   security = FabricSecurity(
       me="Master",
       msp_path="/path/to/msp",
       gateway_path="/path/to/gateway"
   )

   # Access network
   network = security.get_network("mychannel")

   # Access chaincode
   contract = security.get_contract("my_chaincode")

   print(f"Network: {network.channel_name}")
   print(f"Contract: {contract.name}")

|

**Step 3: Submit Transactions**

|

.. code-block:: python

   from wFabricSecurity import FabricSecurity

   security = FabricSecurity(
       me="Master",
       msp_path="/path/to/msp",
       gateway_path="/path/to/gateway"
   )

   # Get contract
   contract = security.get_contract("secure_chaincode")

   # Submit transaction (writes to ledger)
   result = contract.submit_transaction(
       "CreateAsset",
       "asset123",
       "data_payload",
       "Master"
   )
   print(f"Transaction submitted: {result}")

|

**Step 4: Query Ledger**

|

.. code-block:: python

   from wFabricSecurity import FabricSecurity

   security = FabricSecurity(
       me="Master",
       msp_path="/path/to/msp",
       gateway_path="/path/to/gateway"
   )

   contract = security.get_contract("secure_chaincode")

   # Query (read-only, no transaction fees)
   result = contract.evaluate_transaction(
       "ReadAsset",
       "asset123"
   )
   print(f"Asset data: {result}")

|

**Step 5: Complete Fabric Workflow**

|

.. code-block:: python

   from wFabricSecurity import FabricSecurity
   from wFabricSecurity.fabric_security.core.exceptions import (
       CodeIntegrityError,
       PermissionDeniedError
   )

   def secure_fabric_operation():
       # Initialize with full configuration
       security = FabricSecurity(
           me="Master",
           msp_path="/path/to/msp",
           gateway_path="/path/to/gateway"
       )

       # Register identity
       security.register_identity()

       # Register code integrity
       security.register_code(["master.py"], "1.0.0", store_on_ledger=True)

       # Register permissions
       security.register_communication("CN=Master", "CN=Slave")

       # Get contract
       contract = security.get_contract("secure_chaincode")

       # Create and verify message
       message = security.create_message(
           recipient="CN=Slave",
           content='{"action": "process_asset", "asset_id": "123"}'
       )

       if security.verify_message(message):
           # Submit to Fabric
           result = contract.submit_transaction(
               "ProcessAsset",
               message.payload
           )
           return True, result
       else:
           return False, "Verification failed"

   if __name__ == "__main__":
       success, result = secure_fabric_operation()
       print(f"{'✓' if success else '✗'} {result}")

|

|

.. dropdown:: 📊 Architecture Diagram

   .. graphviz::

      digraph FabricFlow {
          rankdir=TB;
          size="8,6";
          
          App [label="Application", shape=box", fillcolor="#667eea", fontcolor="white"];
          Sec [label="FabricSecurity", shape="box", fillcolor="#764ba2", fontcolor="white"];
          GW [label="FabricGateway", shape="box", fillcolor="#2196F3", fontcolor="white"];
          
          subgraph cluster_fabric {
              label="Hyperledger Fabric";
              style="rounded";
              
              NW [label="Network", shape="box"];
              CC [label="Chaincode", shape="box"];
              Ledger [label="Ledger", shape="box"];
          }
          
          App -> Sec -> GW -> NW;
          GW -> CC;
          CC -> Ledger;
      }

|

----

|

.. _tutorial-best-practices:

===============
Best Practices
===============

|

.. dropdown:: 🎯 Security Best Practices

   * **Always verify signatures** before processing messages
   * **Check code integrity** at application startup
   * **Use TLS** for all network communications
   * **Implement rate limiting** to prevent DoS attacks
   * **Store sensitive data** (keys, certs) securely
   * **Rotate credentials** regularly

|

.. dropdown:: 🚀 Performance Best Practices

   * **Enable certificate caching** with appropriate TTL
   * **Use connection pooling** for Fabric gateways
   * **Batch operations** when possible
   * **Monitor rate limits** per participant
   * **Use local storage** for development/testing

|

.. dropdown:: 📝 Logging Best Practices

   * Log all security events (verifications, failures)
   * Include participant IDs in logs
   * Use structured logging format
   * Set appropriate log levels (DEBUG, INFO, WARNING, ERROR)

|

|

.. code-block:: python

   import logging

   # Configure logging
   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
   )

   logger = logging.getLogger(__name__)

   # Use in your code
   logger.info("Security verification successful")
   logger.warning("Rate limit approaching for participant CN=Master")
   logger.error("Code integrity check failed")

|

|

.. seealso::

   * :ref:`api_reference` - Complete API documentation
   * :ref:`getting_started` - Quick start guide
   * :ref:`architecture` - System architecture details
   * :ref:`faq` - Frequently asked questions
