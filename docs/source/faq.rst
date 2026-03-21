===
FAQ
===

Frequently Asked Questions about wFabricSecurity.

|

-----------------
General Questions
-----------------

|

What is Zero Trust?
~~~~~~~~~~~~~~~~~~

**Zero Trust** is a security model that eliminates automatic trust. Every request must be verified, regardless of its origin. In wFabricSecurity:

* Every message is signed and verified
* Every participant's code integrity is checked
* Communication permissions are explicitly granted
* All transactions are recorded immutably

|

What is Hyperledger Fabric?
~~~~~~~~~~~~~~~~~~~~~~~~~~

Hyperledger Fabric is an enterprise-grade permissioned distributed ledger. wFabricSecurity uses Fabric to:

* Store code hashes immutably
* Record participant registrations
* Track task completions
* Provide audit trails

|

Do I need Hyperledger Fabric?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**No**, Fabric is optional. wFabricSecurity includes a local storage fallback that works without Fabric:

|

.. code-block:: python

   # Works without Fabric
   security = FabricSecurity(me="Standalone")
   
   # Automatically uses LocalStorage when Fabric unavailable

|

---------------------
Installation Questions
---------------------

|

How do I install wFabricSecurity?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

|

.. code-block:: bash

   pip install -e .

|

Or clone and install:

|

.. code-block:: bash

   git clone https://github.com/wisrovi/wFabricSecurity.git
   cd wFabricSecurity
   pip install -e .

|

What are the Python version requirements?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Python 3.10 or higher is required.

|

How do I verify the installation?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

|

.. code-block:: python

   python -c "from wFabricSecurity import FabricSecurity; print('OK')"

|

-----------------
Security Questions
-----------------

|

How does code integrity verification work?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

|

#. SHA-256 hash of source files is computed
#. Hash is registered in Fabric (or local storage)
#. Before operations, hash is recomputed and compared
#. If different, ``CodeIntegrityError`` is raised

|

How are signatures verified?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

|

#. Sender signs with their ECDSA private key
#. Receiver gets sender's public certificate
#. Signature is verified using the public key
#. If invalid, ``SignatureError`` is raised

|

What happens if a participant is compromised?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

|

Call ``revoke_participant()`` to immediately block all communications:

|

.. code-block:: python

   security.revoke_participant("CN=CompromisedUser")
   # All future attempts will raise RevocationError

|

--------------------
Performance Questions
--------------------

|

How does rate limiting work?
~~~~~~~~~~~~~~~~~~~~~~~~~~~

|

Token bucket algorithm:

* Tokens added at configured rate (e.g., 100/second)
* Burst allows temporary spikes (e.g., 50 extra requests)
* Tokens consumed on each request
* Returns error when no tokens available

|

How does certificate caching improve performance?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

|

Certificates are cached with TTL:

|

.. code-block:: python

   # First access: fetches from Fabric/MSP
   cert = identity_manager.get_certificate("CN=User")

   # Subsequent accesses: returns from cache
   cert = identity_manager.get_certificate("CN=User")  # Fast!

|

How do retries handle failures?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

|

Exponential backoff:

* Attempt 1: immediate
* Attempt 2: 0.5s delay
* Attempt 3: 1.0s delay
* Attempt 4: 2.0s delay
* ... and so on

|

-----------------------
Configuration Questions
-----------------------

|

How do I configure the library?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

|

Environment variables:

|

.. code-block:: bash

   export FABRIC_PEER_URL=localhost:7051
   export FABRIC_MSP_PATH=/path/to/msp

|

Or ``config.yaml``:

|

.. code-block:: yaml

   fabric_channel: mychannel
   rate_limit_requests_per_second: 100

|

How do I customize rate limits?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

|

.. code-block:: python

   security = FabricSecurity(
       me="Service",
       rate_limit_rps=200,  # 200 requests per second
       rate_limit_burst=100  # Allow 100 extra requests
   )

|

How do I change message TTL?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

|

.. code-block:: python

   security = FabricSecurity(
       me="Service",
       message_ttl=7200  # 2 hours
   )

|

-------------------------
Troubleshooting Questions
-------------------------

|

Why am I getting CodeIntegrityError?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

|

The code has been modified since registration:

|

#. Recompute hash: ``security.compute_code_hash(["file.py"])``
#. Re-register: ``security.register_code(["file.py"], "1.0.1")``

|

Why am I getting PermissionDeniedError?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

|

The communication permission doesn't exist:

|

#. Check permissions: ``security.can_communicate_with(sender, recipient)``
#. Register permission: ``security.register_communication(sender, recipient)``

|

Why is Fabric invoke failing?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

|

Check Fabric status:

|

.. code-block:: bash

   docker ps --filter "name=peer0\|orderer"
   docker logs orderer.net

|

-------------
Common Issues
-------------

|

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Issue
     - Solution
   * - ImportError
     - Run ``pip install -e .``
   * - Certificate not found
     - Verify MSP path is correct
   * - Connection refused
     - Check Fabric network is running
   * - Rate limit exceeded
     - Wait or increase rate_limit_rps
