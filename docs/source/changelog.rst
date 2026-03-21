.. _changelog:

#########
Changelog
#########

All notable changes to wFabricSecurity are documented in this file.

|

.. contents::
   :local:
   :depth: 3

|

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

|

----

|

.. _changelog-v1-0-0:

=============
[1.0.0] - 2026-03-21
=============

|

.. _changelog-v1-0-0-added:

Added
-----

|

* **Comprehensive test suite** with 300+ tests achieving 83%+ code coverage
* **Modular test architecture** with separate test files for each component:
  
  * ``test_main.py`` - Main class tests
  * ``test_core.py`` - Exceptions, enums, and models
  * ``test_config.py`` - Configuration and settings
  * ``test_crypto.py`` - Cryptographic operations
  * ``test_fabric.py`` - Hyperledger Fabric integration
  * ``test_security.py`` - Security services
  * ``test_rate_retry.py`` - Rate limiting and retry logic
  * ``test_storage.py`` - Storage implementations
  * ``test_report_generator.py`` - HTML report generation

* **Professional Sphinx documentation** with:
  
  * ReadTheDocs integration
  * API reference auto-generation
  * Interactive tutorials
  * Architecture diagrams
  * Glossary of terms

* **Security enhancements:**
  
  * ECDSA signature verification with secp256k1
  * SHA-256 code integrity verification
  * Token bucket rate limiting
  * Exponential backoff retry logic

* **Fabric integration improvements:**
  
  * Gateway connection management
  * Network and contract abstraction
  * Certificate caching with LRU eviction
  * Transaction submission support

* **Certificate management:**
  
  * X.509 certificate parsing
  * MSP credential handling
  * Identity verification
  * Certificate caching

|

.. _changelog-v1-0-0-changed:

Changed
-------

|

* **Simplified API** with ``FabricSecuritySimple`` wrapper class
* **Improved error handling** with specific exception types
* **Enhanced type hints** throughout the codebase
* **Better logging** for debugging and monitoring
* **Performance optimizations** for cryptographic operations

|

.. _changelog-v1-0-0-fixed:

Fixed
-----

|

* **conftest.py conflicts** between test directories
* **Test isolation** issues with shared fixtures
* **LSP false positives** for type checking
* **Documentation build warnings** from unsupported theme options

|

.. _changelog-v1-0-0-deprecated:

Deprecated
----------

|

* ``FabricSecurity.register_code_hash()`` - Use ``register_code()`` instead
* ``MessageManager.create_signed_message()`` - Use ``create_message()`` instead

|

----

|

.. _changelog-v0-1-0:

=============
[0.1.0] - 2026-01-15
=============

|

.. _changelog-v0-1-0-added:

Added
-----

|

* Initial release with core functionality
* Basic security services implementation
* Fabric Gateway integration
* Identity management
* Message signing and verification

|

----

|

.. _changelog-types:

==============
Version Types
==============

|

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Type
     - Description
   * - **MAJOR**
     - Breaking changes to the API
   * - **MINOR**
     - New functionality in a backward-compatible manner
   * - **PATCH**
     - Backward-compatible bug fixes

|

|

.. _changelog-branches:

==============
Branch Strategy
==============

|

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Branch
     - Description
   * - ``main``
     - Stable releases
   * - ``develop``
     - Development and integration
   * - ``feature/*``
     - New feature development
   * - ``fix/*``
     - Bug fixes
   * - ``docs/*``
     - Documentation improvements

|

|

.. _changelog-contributing:

==============
Contributing
==============

|

When contributing to wFabricSecurity, please follow these guidelines:

|

**Commit Message Format:**

|

.. code-block:: text

   <type>(<scope>): <subject>
   
   <body>
   
   <footer>

|

**Types:**

|

.. list-table::
   :header-rows: 1

   * - Type
     - Description
   * - ``feat``
     - New feature
   * - ``fix``
     - Bug fix
   * - ``docs``
     - Documentation changes
   * - ``style``
     - Code style changes
   * - ``refactor``
     - Code refactoring
   * - ``test``
     - Adding or updating tests
   * - ``chore``
     - Maintenance tasks

|

**Example:**

|

.. code-block:: text

   feat(security): add certificate revocation list checking
   
   Implemented CRL validation during certificate verification
   to support certificate revocation scenarios.
   
   Fixes #123

|

|

.. seealso::

   * `GitHub Releases <https://github.com/wisrovi/wFabricSecurity/releases>`_
   * :ref:`api_reference` - Complete API documentation
   * :ref:`tutorials` - Implementation guides
