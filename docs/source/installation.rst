============
Installation
============

This guide provides detailed instructions for installing and configuring wFabricSecurity.

|

---------------------------
Standard Installation
---------------------------

|

Clone the Repository
~~~~~~~~~~~~~~~~~~~~

|

.. code-block:: bash

   git clone https://github.com/wisrovi/wFabricSecurity.git
   cd wFabricSecurity

|

Create Virtual Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~

|

.. code-block:: bash

   # Create virtual environment
   python -m venv venv

   # Activate (Linux/Mac)
   source venv/bin/activate

   # Activate (Windows)
   venv\Scripts\activate

|

Install Package
~~~~~~~~~~~~~~

|

.. code-block:: bash

   pip install -e .

|

Install Development Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

|

.. code-block:: bash

   pip install pylint black isort pytest pytest-cov

|

Verify Installation
~~~~~~~~~~~~~~~~~~

|

.. code-block:: python

   python -c "from wFabricSecurity import FabricSecurity; print('Installation successful!')"

|

-------------------
Docker Installation
-------------------

|

Using Docker for development:

|

.. code-block:: dockerfile

   FROM python:3.10-slim

   WORKDIR /app
   COPY . /app
   RUN pip install -e .

   CMD ["python", "-c", "from wFabricSecurity import FabricSecurity; print('OK')"]

|

---------------------------
Hyperledger Fabric Setup
---------------------------

|

Prerequisites
~~~~~~~~~~~~

* Docker Engine 20.10+
* Docker Compose v2+
* 4GB RAM minimum for Fabric

|

Setup Commands
~~~~~~~~~~~~~

|

.. code-block:: bash

   cd enviroment

   # Generate certificates and artifacts
   make setup

   # Start Docker network
   make up

   # Verify network status
   docker ps

|

---------------
Configuration
---------------

|

Environment Variables
~~~~~~~~~~~~~~~~~~~~

|

Set these environment variables for production deployments:

|

.. code-block:: bash

   # Required for Fabric integration
   export FABRIC_PEER_URL=localhost:7051
   export FABRIC_MSP_PATH=/path/to/msp
   export FABRIC_CHANNEL=mychannel
   export FABRIC_CHAINCODE=tasks

   # Optional: Rate limiting
   export RATE_LIMIT_RPS=100
   export RETRY_MAX_ATTEMPTS=3

|

Configuration File
~~~~~~~~~~~~~~~~~

|

Create a ``config.yaml`` file:

|

.. code-block:: yaml

   # Local Storage
   local_data_dir: /tmp/fabric_security_data

   # Fabric Configuration
   fabric_channel: mychannel
   fabric_chaincode: tasks
   fabric_peer_url: localhost:7051

   # Retry Settings
   retry_max_attempts: 3
   retry_backoff_factor: 1.5
   retry_initial_delay: 0.5

   # Rate Limiting
   rate_limit_requests_per_second: 100
   rate_limit_burst: 200

   # Message Settings
   message_ttl_seconds: 3600

   # Certificate Cache
   cert_cache_size: 100
   cert_cache_ttl_seconds: 3600

|

---------------
Troubleshooting
---------------

|

Installation Issues
~~~~~~~~~~~~~~~~~~

|

.. list-table::
   :header-rows: 1

   * - Issue
     - Solution
   * - ``ImportError: No module named wFabricSecurity``
     - Run ``pip install -e .`` in the project root
   * - ``Permission denied``
     - Use ``pip install --user`` or virtual environment
   * - ``cryptography`` module not found
     - Run ``pip install cryptography``

|

Fabric Issues
~~~~~~~~~~~~~

|

.. list-table::
   :header-rows: 1

   * - Issue
     - Solution
   * - Docker containers not starting
     - Run ``docker system prune`` and restart
   * - Connection refused
     - Verify Fabric network is running with ``docker ps``
   * - Certificate errors
     - Regenerate certificates with ``make clean && make setup``
