.. wFabricSecurity documentation master file
   :numbered:
   :maxdepth: 4
   :html_theme.sidebar_secondary: <p><a href="https://pypi.org/project/wFabricSecurity/">PyPI Package</a></p>
   :html_theme.toc_page_number: true

|

====================================
Welcome to wFabricSecurity |version|
====================================

**wFabricSecurity** is a comprehensive Zero Trust Security System designed for Hyperledger Fabric environments. This library implements cryptographic identity verification, code integrity validation, communication permissions, and message integrity checks.

|

.. image:: https://img.shields.io/badge/Python-3.10+-blue.svg
   :target: https://www.python.org/
   :alt: Python Version

.. image:: https://img.shields.io/badge/License-MIT-green.svg
   :target: https://github.com/wisrovi/wFabricSecurity/blob/main/LICENSE
   :alt: License

.. image:: https://img.shields.io/readthedocs/wFabricSecurity/latest?style=flat
   :target: https://wFabricSecurity.readthedocs.io/
   :alt: Documentation Status

.. image:: https://img.shields.io/github/actions/workflow/status/wisrovi/wFabricSecurity/tests.yml?branch=main
   :target: https://github.com/wisrovi/wFabricSecurity/actions
   :alt: Build Status

|

---------
Overview
---------

wFabricSecurity implements a **Zero Trust** security model where no participant is automatically trusted. Every transaction must be cryptographically verified before processing.

This library provides:

* **Code Integrity Verification** - SHA-256 hash verification of source code to detect tampering
* **Cryptographic Signatures** - ECDSA signing and verification for message authenticity
* **Communication Permissions** - Fine-grained access control with bidirectional, outbound, and inbound options
* **Message Integrity** - Hash verification to detect transmission alterations
* **Rate Limiting** - Token bucket algorithm for DoS protection
* **Retry Logic** - Exponential backoff with configurable attempts
* **Certificate Caching** - LRU cache with TTL for performance optimization

|

-------------
Key Features
-------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Feature
     - Description
   * - **Zero Trust Model**
     - Every participant and transaction must be verified before processing
   * - **Code Integrity**
     - SHA-256 hash verification of source code to detect tampering
   * - **ECDSA Signatures**
     - Elliptic curve cryptography for message signing and verification
   * - **Communication Permissions**
     - Fine-grained access control (bidirectional, outbound, inbound)
   * - **Message Integrity**
     - Hash verification to detect transmission alterations
   * - **Rate Limiting**
     - Token bucket algorithm for DoS protection
   * - **Retry Logic**
     - Exponential backoff with configurable attempts
   * - **Certificate Caching**
     - LRU cache with TTL for performance optimization

|

-------------
Architecture
-------------

wFabricSecurity follows a modular architecture with clear separation of concerns:

|

.. mermaid::

   flowchart TB
       subgraph Presentation["Presentation Layer"]
           CLI[CLI Tool]
           API[API Gateway]
       end

       subgraph Application["Application Layer"]
           FS[FabricSecurity]
           FSS[FabricSecuritySimple]
       end

       subgraph Security["Security Layer"]
           IV[IntegrityVerifier]
           PM[PermissionManager]
           MM[MessageManager]
           RL[RateLimiter]
       end

       subgraph Crypto["Cryptographic Layer"]
           HS[HashingService]
           SS[SigningService]
           IM[IdentityManager]
       end

       CLI --> FS
       API --> FS
       FS --> IV & PM & MM & RL
       IV --> HS & SS
       SS --> IM

|

--------
Quick Start
--------

|

Install the package:

|

.. code-block:: bash

   pip install wFabricSecurity

|

Basic usage example:

|

.. code-block:: python

   from wFabricSecurity import FabricSecurity

   # Initialize security system
   security = FabricSecurity(
       me="Master",
       msp_path="/path/to/msp"
   )

   # Register identity and code
   security.register_identity()
   security.register_code(["master.py"], "1.0.0")

   # Register communication permissions
   security.register_communication("CN=Master", "CN=Slave")

   # Create and verify signed message
   message = security.create_message(
       recipient="CN=Slave",
       content='{"operation": "process_data"}'
   )

   if security.verify_message(message):
       print("Message is authentic and unaltered")

|

---------------
Zero Trust Flow
---------------

|

.. mermaid::

   sequenceDiagram
       participant M as Master
       participant G as FabricGateway
       participant F as Hyperledger Fabric
       participant S as Slave

       M->>M: 1. Compute SHA-256 hash_a
       M->>M: 2. Sign hash_a with ECDSA
       M->>S: 3. POST {payload, hash_a, sig}

       S->>S: 4. Verify signature
       S->>S: 5. Check permissions

       S->>G: 6. Query code_hash
       G->>F: 7. GetParticipant
       F-->>G: 8. Return data
       G-->>S: 9. Return code_hash

       alt Code Modified
           S->>S: 10a. Raise CodeIntegrityError
       else Code Valid
           S->>S: 10b. Process payload
           S->>G: 11. CompleteTask
           G->>F: 12. Invoke chaincode
       end

|

---------------
Documentation
---------------

|

.. toctree::
   :maxdepth: 3
   :caption: Contents
   :numbered:

   getting_started
   installation
   usage
   api_reference
   tutorials
   faq
   bibliography

|

-------------------
Indices and Tables
-------------------

|

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

|

--------
Citation
--------

|

If you use wFabricSecurity in your research, please cite:

|

.. code-block:: bibtex

   @software{wFabricSecurity,
     author = {William Rodriguez},
     title = {wFabricSecurity: Zero Trust Security System for Hyperledger Fabric},
     url = {https://github.com/wisrovi/wFabricSecurity},
     version = {1.0.0},
     year = {2026},
   }

|

--------
Author
--------

|

**William Rodriguez**

* GitHub: https://github.com/wisrovi
* LinkedIn: https://es.linkedin.com/in/wisrovi-rodriguez
* Email: william.rodriguez@ecapturedtech.com

|

--------
License
--------

|

This project is licensed under the MIT License.

| Copyright (c) 2026 William Rodriguez

|

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

|

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

|

**THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.**

|

----

*Last updated: |today|*
