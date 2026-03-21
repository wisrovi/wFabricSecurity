Tutorials
==========

This section provides step-by-step tutorials for common use cases.

Tutorial 1: Basic Master-Slave Communication
---------------------------------------------

Objective
~~~~~~~~~

Set up a basic Master-Slave communication with Zero Trust verification.

Steps
~~~~~~

1. **Initialize Master Node**

   .. code-block:: python

      from wFabricSecurity import FabricSecurity

      master = FabricSecurity(me="CN=Master")

      # Register identity
      master.register_identity()

      # Register code
      master.register_code(["master.py"], "1.0.0")

2. **Initialize Slave Node**

   .. code-block:: python

      from wFabricSecurity import FabricSecurity

      slave = FabricSecurity(me="CN=Slave")

      # Register identity
      slave.register_identity()

      # Register code
      slave.register_code(["slave.py"], "1.0.0")

3. **Configure Permissions**

   .. code-block:: python

      # On master node
      master.register_communication("CN=Master", "CN=Slave")

4. **Send Audited Message**

   .. code-block:: python

      message = master.create_message(
          recipient="CN=Slave",
          content='{"task": "process_data", "payload": {...}}'
      )

      # Send to slave via HTTP, etc.

5. **Verify and Process on Slave**

   .. code-block:: python

      # On slave node
      if slave.verify_message(message):
          # Process the message
          result = process(message.content)
      else:
          # Reject the message
          raise SecurityError("Invalid message")

Tutorial 2: Rate-Limited API
----------------------------

Objective
~~~~~~~~~

Create an API endpoint with rate limiting and retry logic.

Setup
~~~~~~

.. code-block:: python

   from wFabricSecurity import RateLimiter, with_retry

   # Configure rate limiter
   limiter = RateLimiter(requests_per_second=100, burst=50)

   # Configure retry decorator
   @with_retry(max_attempts=3, backoff_factor=2.0)
   def process_request(data):
       # Process with potential Fabric call
       return fabric_invoke("ProcessTask", data)

Decorator Usage
~~~~~~~~~~~~~~~

.. code-block:: python

   def api_endpoint(request):
       # Check rate limit
       if not limiter.try_acquire():
           return {"error": "Rate limit exceeded"}, 429

       # Process with retry
       try:
           result = process_request(request.data)
           return {"result": result}, 200
       except Exception as e:
           return {"error": str(e)}, 500

Tutorial 3: Code Integrity Verification
-----------------------------------------

Objective
~~~~~~~~~

Implement automatic code integrity verification for sensitive operations.

Setup
~~~~~~

.. code-block:: python

   from wFabricSecurity import IntegrityVerifier, FabricGateway

   gateway = FabricGateway(msp_path="/path/to/msp")
   verifier = IntegrityVerifier(gateway)

   # Register code on startup
   verifier.register_code(["sensitive_module.py"], "1.0.0")

Verification Middleware
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def verify_before_operation(operation_func):
       def wrapper(*args, **kwargs):
           # Verify code integrity
           if not verifier.verify_code_integrity(["sensitive_module.py"]):
               raise CodeIntegrityError("Code integrity check failed")

           # Proceed with operation
           return operation_func(*args, **kwargs)
       return wrapper

   @verify_before_operation
   def process_sensitive_data(data):
       # This code is verified before execution
       return expensive_operation(data)

Tutorial 4: Message Expiration and Cleanup
-----------------------------------------

Objective
~~~~~~~~~

Implement automatic message expiration for temporary data.

Setup
~~~~~~

.. code-block:: python

   from wFabricSecurity import MessageManager, DataType

   manager = MessageManager(gateway, ttl_seconds=3600)

Creating Messages with TTL
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Create message that expires in 1 hour
   msg = manager.create_message(
       sender="CN=Master",
       recipient="CN=Slave",
       content="Temporary data",
       data_type=DataType.JSON,
       ttl_seconds=3600
   )

   print(f"Expires at: {msg.expires_at}")

Automatic Cleanup
~~~~~~~~~~~~~~~~

.. code-block:: python

   # Schedule periodic cleanup
   import threading
   import time

   def cleanup_task():
       while True:
           count = manager.cleanup_expired_messages()
           if count > 0:
               print(f"Cleaned up {count} expired messages")
           time.sleep(60)  # Run every minute

   cleanup_thread = threading.Thread(target=cleanup_task, daemon=True)
   cleanup_thread.start()

Tutorial 5: Participant Revocation
----------------------------------

Objective
~~~~~~~~~

Implement immediate participant revocation for compromised identities.

Setup
~~~~~~

.. code-block:: python

   from wFabricSecurity import PermissionManager, RevocationError

   manager = PermissionManager(gateway)

Register Participant
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   manager.register_participant({
       "identity": "CN=CompromisedUser",
       "code_hash": "sha256:abc123...",
       "allowed_communications": ["CN=OtherUser"]
   })

Revoke Participant
~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Immediate revocation
   manager.revoke_participant("CN=CompromisedUser")

   # All future communications will be denied
   try:
       manager.can_communicate_with("CN=CompromisedUser", "CN=OtherUser")
   except RevocationError:
       print("Participant has been revoked!")
