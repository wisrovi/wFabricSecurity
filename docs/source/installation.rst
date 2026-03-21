.. _installation:

============
Installation
============

This guide provides detailed instructions for installing and configuring wFabricSecurity.

|

.. contents::
   :local:
   :depth: 3

|

|

----

|

.. _installation-requirements:

============
Requirements
============

|

.. _installation-python:

Python
------

|

wFabricSecurity requires **Python 3.10** or higher.

|

.. code-block:: bash

   # Check your Python version
   python --version

   # If you need to install Python 3.10+
   # Visit: https://www.python.org/downloads/

|

|

.. _installation-os:

Operating System
----------------

|

wFabricSecurity is tested and supported on:

|

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - OS
     - Status
   * - **Ubuntu 20.04+**
     - ✅ Fully supported
   * - **Debian 11+**
     - ✅ Fully supported
   * - **macOS 11+**
     - ✅ Fully supported
   * - **Windows 10+**
     - ✅ Fully supported
   * - **Windows Subsystem for Linux**
     - ✅ Fully supported

|

|

.. _installation-optional:

Optional Dependencies
---------------------

|

For full functionality, you may also need:

|

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Dependency
     - Required For
   * - **Hyperledger Fabric Gateway SDK**
     - Fabric network integration
   * - **OpenSSL**
     - Certificate operations
   * - **Git**
     - Installing from source

|

|

----

|

.. _installation-pip:

==============
Installation via pip
==============

|

The easiest way to install wFabricSecurity is using pip:

|

.. code-block:: bash

   # Standard installation
   pip install wFabricSecurity

   # With minimal dependencies
   pip install wFabricSecurity --no-deps

   # Specific version
   pip install wFabricSecurity==1.0.0

   # Upgrade to latest version
   pip install --upgrade wFabricSecurity

|

|

.. _installation-venv:

Virtual Environment (Recommended)
---------------------------------

|

It's recommended to install wFabricSecurity in a virtual environment:

|

.. code-block:: bash

   # Create a virtual environment
   python -m venv wfabric-env

   # Activate it (Linux/macOS)
   source wfabric-env/bin/activate

   # Activate it (Windows)
   wfabric-env\Scripts\activate

   # Install wFabricSecurity
   pip install wFabricSecurity

|

|

----

|

.. _installation-source:

===============
Installation from Source
===============

|

To install from source for development or testing:

|

.. _installation-clone:

Clone the Repository
--------------------

|

.. code-block:: bash

   git clone https://github.com/wisrovi/wFabricSecurity.git
   cd wFabricSecurity

|

|

.. _installation-editable:

Editable Install
----------------

|

For development, install in editable mode:

|

.. code-block:: bash

   pip install -e .

|

|

.. _installation-dev:

Development Install
-------------------

|

Install with all development dependencies:

|

.. code-block:: bash

   pip install -e ".[dev]"

|

This includes:

|

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Package
     - Purpose
   * - **pytest**
     - Testing framework
   * - **pytest-cov**
     - Code coverage
   * - **pytest-asyncio**
     - Async testing
   * - **black**
     - Code formatting
   * - **ruff**
     - Linting
   * - **sphinx**
     - Documentation

|

|

----

|

.. _installation-docker:

==============
Docker Installation
==============

|

You can also run wFabricSecurity in a Docker container:

|

.. code-block:: dockerfile

   FROM python:3.11-slim

   WORKDIR /app

   # Install wFabricSecurity
   RUN pip install wFabricSecurity

   # Copy your application
   COPY . /app

   # Run your application
   CMD ["python", "your_app.py"]

|

Build and run:

|

.. code-block:: bash

   # Build the image
   docker build -t my-wfabric-app .

   # Run the container
   docker run -v /path/to/msp:/app/msp my-wfabric-app

|

|

----

|

.. _installation-verify:

===============
Verification
===============

|

After installation, verify everything is working:

|

.. code-block:: bash

   # Verify Python import
   python -c "from wFabricSecurity import FabricSecurity; print('✓ Import successful')"

   # Run version check
   python -c "import wFabricSecurity; print(f'Version: {wFabricSecurity.__version__}')"

   # Run built-in tests
   pytest --co -q

|

|

----

|

.. _installation-config:

===============
Configuration
===============

|

.. _installation-msp:

MSP Configuration
-----------------

|

The Membership Service Provider (MSP) contains your cryptographic credentials:

|

.. code-block:: text

   msp/
   ├── cacerts/           # CA certificates
   ├── signcerts/         # Signing certificates
   ├── keystore/          # Private keys
   ├── admincerts/         # Admin certificates
   └── tlscacerts/         # TLS CA certificates

|

Typical MSP path:

|

.. code-block:: python

   # Production
   msp_path = "/etc/hyperledger/msp"

   # Development
   msp_path = "./test/msp"

   # Docker
   msp_path = "/fabric/msp"

|

|

.. _installation-gateway:

Gateway Configuration
--------------------

|

For Fabric integration, you'll need a gateway connection profile:

|

.. code-block:: yaml

   # connection-profile.yaml
   name: "my-network"
   version: "1.0"
   client:
     organization: "Org1"
     connection:
       timeout:
         peer:
           endorser: 300
         orderer:
           deliver: 300
   channels:
     mychannel:
       peers:
         peer0.org1.example.com: {}

|

|

----

|

.. _installation-troubleshooting:

===============
Troubleshooting
===============

|

.. _installation-error-import:

Import Errors
-------------

|

If you encounter import errors:

|

.. code-block:: bash

   # Upgrade pip
   pip install --upgrade pip

   # Reinstall wFabricSecurity
   pip uninstall wFabricSecurity
   pip install wFabricSecurity

   # Check installed packages
   pip list | grep -i fabric

|

|

.. _installation-error-cryptography:

Cryptography Errors
-------------------

|

If cryptography-related errors occur:

|

.. code-block:: bash

   # Upgrade cryptography
   pip install --upgrade cryptography

   # Install build tools (Linux)
   sudo apt-get install build-essential python3-dev libssl-dev

   # Reinstall
   pip uninstall cryptography wFabricSecurity
   pip install wFabricSecurity

|

|

.. _installation-error-permissions:

Permission Errors
------------------

|

On Linux/macOS, you may need:

|

.. code-block:: bash

   # Fix pip permissions
   pip install --user wFabricSecurity

   # Or use a virtual environment
   python -m venv env
   source env/bin/activate
   pip install wFabricSecurity

|

|

----

|

.. _installation-uninstall:

===============
Uninstallation
===============

|

To remove wFabricSecurity:

|

.. code-block:: bash

   # Uninstall via pip
   pip uninstall wFabricSecurity

   # Remove virtual environment (if created)
   rm -rf wfabric-env

|

|

----

|

.. seealso::

   * :ref:`getting_started` - Quick start guide
   * :ref:`tutorials` - Step-by-step tutorials
   * :ref:`api_reference` - API documentation
