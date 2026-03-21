.. include:: ../README.md
   :start-line: 1
   :end-line: 50

===============
Getting Started
===============

This guide will help you get started with wFabricSecurity.

|

-------------
Prerequisites
-------------

Before installing wFabricSecurity, ensure you have:

* **Python 3.10+** - wFabricSecurity requires Python 3.10 or higher
* **pip** - Python package manager
* **Git** - For cloning the repository

|

Optional Requirements
~~~~~~~~~~~~~~~~~~~~

* **Docker & Docker Compose** - For running Hyperledger Fabric
* **Hyperledger Fabric 2.x** - For blockchain backend storage

|

-------------
Core Concepts
-------------

|

Zero Trust Model
~~~~~~~~~~~~~~~

wFabricSecurity implements a Zero Trust security model with the following principles:

1. **Never Trust, Always Verify** - Every request must be authenticated
2. **Least Privilege** - Participants only have necessary permissions
3. **Assume Breach** - All communications are encrypted and verified

|

Key Components
~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Component
     - Description
   * - ``FabricSecurity``
     - Main class implementing complete Zero Trust security
   * - ``FabricGateway``
     - Gateway for Hyperledger Fabric communication
   * - ``IntegrityVerifier``
     - Verifies code integrity using SHA-256
   * - ``PermissionManager``
     - Manages communication permissions
   * - ``RateLimiter``
     - Token bucket rate limiting for DoS protection

|

-------------
First Steps
-------------

|

#. Install the package
#. Initialize the security system
#. Register your identity and code
#. Configure communication permissions
#. Start creating and verifying messages

|

-------------
Quick Example
-------------

|

Here's a complete example demonstrating the core workflow:

|

.. code-block:: python

   from wFabricSecurity import FabricSecurity

   # Initialize the security system
   security = FabricSecurity(
       me="MyService",
       msp_path="/path/to/msp"
   )

   # Step 1: Register your identity
   security.register_identity()

   # Step 2: Register your code with a hash
   security.register_code(["my_service.py"], "1.0.0")

   # Step 3: Register communication permissions
   security.register_communication("CN=MyService", "CN=OtherService")

   # Step 4: Create a signed message
   message = security.create_message(
       recipient="CN=OtherService",
       content='{"operation": "process", "data": "example"}'
   )

   # Step 5: Verify the message (on the receiving end)
   if security.verify_message(message):
       print("Message is authentic and unaltered!")

|

-------------
Next Steps
-------------

|

* Continue to :doc:`installation` for detailed setup instructions
* See :doc:`usage` for practical examples
* Explore :doc:`api_reference` for complete API documentation
