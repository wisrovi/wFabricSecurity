Usage Examples
===============

This section provides practical examples for using wFabricSecurity.

Basic Zero Trust System
-----------------------

Complete Security Workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from wFabricSecurity import FabricSecurity

   # Initialize
   security = FabricSecurity(
       me="Master",
       msp_path="/path/to/msp"
   )

   # Register identity
   security.register_identity()

   # Register code with hash
   security.register_code(["master.py"], "1.0.0")

   # Register communication permissions
   security.register_communication("CN=Master", "CN=Slave")

   # Create signed message
   message = security.create_message(
       recipient="CN=Slave",
       content='{"operation": "process_data"}'
   )

   # Verify message
   if security.verify_message(message):
       print("Message is authentic!")

Code Integrity
-------------

Registering and Verifying Code
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from wFabricSecurity import FabricSecurity, CodeIntegrityError

   security = FabricSecurity(me="Service")

   # Register your code
   security.register_code(["my_service.py", "helpers.py"], "1.0.0")

   # Verify code integrity (automatic)
   if security.verify_code():
       print("Code is intact!")

   # Manual verification
   is_valid = security.verify_code(["my_service.py"])
   print(f"Code valid: {is_valid}")

   # Detect tampering
   try:
       security.verify_code(["modified_file.py"])
   except CodeIntegrityError:
       print("Code has been tampered with!")

Digital Signatures
-----------------

ECDSA Signing and Verification
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from wFabricSecurity import SigningService

   service = SigningService(private_key=None)  # Uses MSP key

   # Sign data
   data = "Important data to sign"
   signer_id = "CN=Master"
   signature = service.sign(data, signer_id)

   print(f"Signature: {signature[:50]}...")

   # Verify signature
   def cert_getter(signer_id):
       return "certificate_pem"

   is_valid = service.verify(data, signature, cert_getter, signer_id)
   print(f"Signature valid: {is_valid}")

Communication Permissions
-----------------------

Permission Management
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from wFabricSecurity import FabricSecurity, PermissionDeniedError

   security = FabricSecurity(me="Master")

   # Register communication permission
   security.register_communication("CN=Master", "CN=Slave")

   # Check permission
   can_communicate = security.can_communicate_with("CN=Master", "CN=Slave")
   print(f"Communication allowed: {can_communicate}")

   # Permission enforcement
   try:
       if not security.can_communicate_with("Unknown", "CN=Slave"):
           raise PermissionDeniedError("Not authorized")
   except PermissionDeniedError as e:
       print(f"Permission denied: {e}")

Rate Limiting
-------------

Token Bucket Rate Limiter
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from wFabricSecurity import RateLimiter, RateLimitError

   # Create rate limiter
   limiter = RateLimiter(requests_per_second=100, burst=50)

   # Blocking acquire
   limiter.acquire()
   limiter.acquire()

   # Non-blocking try_acquire
   if limiter.try_acquire():
       process_request()
   else:
       print("Rate limit exceeded, try again later")

   # Get statistics
   stats = limiter.get_stats()
   print(f"Available tokens: {stats['available_tokens']}")
   print(f"Recent requests (1s): {stats['recent_requests_1s']}")

Retry Logic
-----------

Exponential Backoff
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from wFabricSecurity import with_retry

   @with_retry(max_attempts=3, backoff_factor=2.0, initial_delay=0.1)
   def unreliable_fabric_call():
       # Simulate potential failure
       import random
       if random.random() < 0.5:
           raise ConnectionError("Fabric temporarily unavailable")
       return "success"

   # Use the function
   result = unreliable_fabric_call()
   print(f"Result: {result}")

Message Management
-----------------

Creating and Verifying Messages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from wFabricSecurity import MessageManager, DataType

   manager = MessageManager(gateway, ttl_seconds=3600)

   # Create message with TTL
   msg = manager.create_message(
       sender="CN=Master",
       recipient="CN=Slave",
       content="Sensitive data",
       data_type=DataType.JSON,
       ttl_seconds=3600
   )

   # Verify message integrity
   is_valid = manager.verify_message(msg)
   print(f"Message valid: {is_valid}")

   # Cleanup expired messages
   expired_count = manager.cleanup_expired_messages()
   print(f"Cleaned up {expired_count} expired messages")

Master-Slave Decorators
------------------------

Audited Task Delegation
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from wFabricSecurity import FabricSecuritySimple

   security = FabricSecuritySimple(me="Master")

   # MASTER: Decorator for audited task sending
   @security.master_audit(
       task_prefix="TASK",
       trusted_slaves=["CN=Slave1", "CN=Slave2"]
   )
   def send_to_slave(payload, task_id, hash_a, sig, my_id):
       """This function is automatically signed and audited."""
       return http_post("http://slave/process", payload)

   # SLAVE: Decorator for verified task receiving
   @security.slave_verify(trusted_masters=["CN=Master"])
   def process_task(payload):
       """Automatically verifies Master's identity and code."""
       return process(payload)

   # Usage
   result = send_to_slave({"data": "value"})
