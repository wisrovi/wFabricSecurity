.. wFabricSecurity documentation master file
   :numbered:
   :maxdepth: 4
   :html_theme.sidebar_secondary: <p><a href="https://pypi.org/project/wFabricSecurity/">PyPI Package</a></p>
   :html_theme.toc_page_number: true
   :canonical_url: https://wFabricSecurity.readthedocs.io/en/latest/

|

.. raw:: html

    <style>
        .hero-section {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 3rem 2rem;
            border-radius: 12px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
        }
        .hero-section h1 {
            color: white;
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }
        .hero-section p {
            font-size: 1.2rem;
            opacity: 0.95;
            max-width: 700px;
            margin: 0 auto 1.5rem;
        }
        .hero-section .official-url {
            background: rgba(255,255,255,0.2);
            padding: 15px 25px;
            border-radius: 8px;
            margin: 1.5rem auto;
            max-width: 600px;
        }
        .hero-section .official-url a {
            color: #fff;
            font-weight: bold;
            text-decoration: underline;
        }
        .badge-row {
            display: flex;
            justify-content: center;
            gap: 1rem;
            flex-wrap: wrap;
            margin-top: 1rem;
        }
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
        }
        .feature-card {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        .feature-card h3 {
            margin-top: 0;
            color: #333;
        }
        .feature-card p {
            color: #666;
            margin-bottom: 0;
        }
        .quick-start {
            background: #f0f4ff;
            padding: 2rem;
            border-radius: 8px;
            margin: 2rem 0;
        }
        .code-example {
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 1.5rem;
            border-radius: 8px;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            font-size: 0.9rem;
        }
        .stats-row {
            display: flex;
            justify-content: space-around;
            margin: 2rem 0;
            text-align: center;
        }
        .stat-item h2 {
            font-size: 2.5rem;
            color: #667eea;
            margin: 0;
        }
        .stat-item p {
            margin: 0.5rem 0 0;
            color: #666;
        }
        .official-banner {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
            padding: 2rem;
            border-radius: 12px;
            text-align: center;
            margin: 2rem 0;
        }
        .official-banner h3 {
            color: white;
            margin-bottom: 1rem;
        }
        .official-banner a {
            background: white;
            color: #11998e;
            padding: 12px 30px;
            border-radius: 25px;
            text-decoration: none;
            font-weight: bold;
            display: inline-block;
            margin-top: 1rem;
        }
        .official-banner a:hover {
            transform: scale(1.05);
        }
    </style>

|

.. raw:: html

    <div class="hero-section">
        <h1>🛡️ wFabricSecurity</h1>
        <p>Zero Trust Security System for Hyperledger Fabric.<br>
        Cryptographic identity verification, code integrity validation, and secure communication.</p>
        <div class="official-url">
            <strong>📚 Official Documentation:</strong><br>
            <a href="https://wFabricSecurity.readthedocs.io/en/latest/">https://wFabricSecurity.readthedocs.io/en/latest/</a>
        </div>
        <div class="badge-row">
            <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python 3.10+">
            <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT License">
            <img src="https://readthedocs.org/projects/wfabricsecurity/badge/?version=latest" alt="Documentation Status">
            <img src="https://img.shields.io/github/actions/workflow/status/wisrovi/wFabricSecurity/tests.yml?branch=main" alt="Build Status">
            <img src="https://img.shields.io/codecov/c/github/wisrovi/wFabricSecurity/main" alt="Coverage">
        </div>
    </div>

|

.. raw:: html

    <div class="official-banner">
        <h3>📚 Complete Documentation Available</h3>
        <p>For comprehensive tutorials, API reference, architecture diagrams, and FAQ,<br>
        visit the official documentation:</p>
        <p style="font-size: 1.2em; margin-top: 1rem;">
            <strong><a href="https://wFabricSecurity.readthedocs.io/en/latest/" style="color: white;">https://wFabricSecurity.readthedocs.io/en/latest/</a></strong>
        </p>
        <a href="https://wFabricSecurity.readthedocs.io/en/latest/" target="_blank">📖 Open Official Documentation →</a>
    </div>

|

----

|

.. _overview:

========
Overview
========

**wFabricSecurity** implements a comprehensive **Zero Trust** security model where no participant is automatically trusted. Every transaction must be cryptographically verified before processing.

In a Zero Trust architecture:

* **Never Trust, Always Verify** - Every request is authenticated and authorized
* **Least Privilege Access** - Users get minimum necessary permissions
* **Assume Breach** - Continuous validation and monitoring

|

.. _features:

==========
Key Features
==========

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Feature
     - Description
   * - **Zero Trust Model**
     - Every participant and transaction must be verified before processing
   * - **Code Integrity**
     - SHA-256 hash verification of source code to detect tampering
   * - **ECDSA Signatures**
     - Elliptic curve cryptography (secp256k1) for message signing and verification
   * - **Communication Permissions**
     - Fine-grained access control with bidirectional, outbound, and inbound options
   * - **Message Integrity**
     - Hash verification to detect transmission alterations
   * - **Rate Limiting**
     - Token bucket algorithm for DoS protection with configurable rates
   * - **Retry Logic**
     - Exponential backoff with jitter for resilient network communication
   * - **Certificate Caching**
     - LRU cache with TTL for performance optimization
   * - **Hyperledger Fabric Integration**
     - Seamless integration with Fabric Gateway API and network management

|

----

|

.. _architecture:

==========
Architecture
==========

wFabricSecurity follows a **layered modular architecture** with clear separation of concerns:

|

.. graphviz::

    digraph Architecture {
        rankdir=LR;
        size="8,5";
        node [shape=box, style="rounded,filled", fontname="Helvetica"];
        
        User [fillcolor="#667eea", fontcolor="white"];
        API [fillcolor="#764ba2", fontcolor="white"];
        
        subgraph cluster_app {
            label="Application Layer";
            style="rounded";
            FS [label="FabricSecurity", fillcolor="#4CAF50", fontcolor="white"];
            FSS [label="FabricSecuritySimple", fillcolor="#4CAF50", fontcolor="white"];
        }
        
        subgraph cluster_security {
            label="Security Layer";
            style="rounded";
            IV [label="IntegrityVerifier", fillcolor="#FF9800", fontcolor="white"];
            PM [label="PermissionManager", fillcolor="#FF9800", fontcolor="white"];
            MM [label="MessageManager", fillcolor="#FF9800", fontcolor="white"];
            RL [label="RateLimiter", fillcolor="#FF9800", fontcolor="white"];
        }
        
        subgraph cluster_crypto {
            label="Cryptographic Layer";
            style="rounded";
            HS [label="HashingService", fillcolor="#2196F3", fontcolor="white"];
            SS [label="SigningService", fillcolor="#2196F3", fontcolor="white"];
            IM [label="IdentityManager", fillcolor="#2196F3", fontcolor="white"];
        }
        
        subgraph cluster_fabric {
            label="Fabric Layer";
            style="rounded";
            GW [label="FabricGateway", fillcolor="#9C27B0", fontcolor="white"];
            NW [label="FabricNetwork", fillcolor="#9C27B0", fontcolor="white"];
            CT [label="FabricContract", fillcolor="#9C27B0", fontcolor="white"];
        }
        
        subgraph cluster_storage {
            label="Storage Layer";
            style="rounded";
            LS [label="LocalStorage", fillcolor="#607D8B", fontcolor="white"];
            FSs [label="FabricStorage", fillcolor="#607D8B", fontcolor="white"];
        }
        
        User -> API;
        API -> FS;
        API -> FSS;
        FS -> IV -> HS;
        FS -> IV -> SS -> IM;
        FS -> PM;
        FS -> MM;
        FS -> RL;
        FS -> GW -> NW;
        FS -> GW -> CT;
        FS -> LS;
        FS -> FSs;
    }

|

----

|

.. _quick-start:

==========
Quick Start
==========

|

Install wFabricSecurity:

|

.. code-block:: bash

    pip install wFabricSecurity

|

Create a secure Fabric interaction:

|

.. code-block:: python

    from wFabricSecurity import FabricSecurity

    # Initialize security system
    security = FabricSecurity(
        me="Master",
        msp_path="/path/to/msp",
        gateway_path="/path/to/gateway"
    )

    # Register identity and code integrity
    security.register_identity()
    security.register_code(["master.py"], "1.0.0")

    # Define communication permissions
    security.register_communication("CN=Master", "CN=Slave")

    # Create and send a signed message
    message = security.create_message(
        recipient="CN=Slave",
        content='{"operation": "process_data", "data_id": "12345"}'
    )

    # Verify and process
    if security.verify_message(message):
        print("✓ Message is authentic and unaltered")

|

Or use the simplified interface:

|

.. code-block:: python

    from wFabricSecurity import FabricSecuritySimple

    security = FabricSecuritySimple(msp_path="/path/to/msp")

    # One-line verification
    result = security.verify_and_process(
        payload={"action": "update"},
        sender="CN=Master"
    )
    
    print(f"Verification result: {result}")

|

----

|

.. _security-flow:

=============
Security Flow
============

|

.. graphviz::

    digraph SecurityFlow {
        rankdir=TB;
        size="10,12";
        node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=11];
        
        Start [label="Start", shape=ellipse, fillcolor="#4CAF50", fontcolor="white"];
        CreateHash [label="1. Compute SHA-256 Hash", fillcolor="#E3F2FD"];
        Sign [label="2. Sign with ECDSA", fillcolor="#E3F2FD"];
        Send [label="3. Send {payload, hash, signature}", fillcolor="#FFF3E0"];
        Receive [label="Receive Message", fillcolor="#E8F5E9"];
        VerifySig [label="4. Verify Signature", fillcolor="#FFEBEE"];
        CheckPerm [label="5. Check Permissions", fillcolor="#FFEBEE"];
        QueryHash [label="6. Query Code Hash from Fabric", fillcolor="#F3E5F5"];
        GetData [label="7. GetParticipant from Ledger", fillcolor="#F3E5F5"];
        Compare [label="8. Compare Hashes", fillcolor="#E3F2FD"];
        Invalid [label="❌ Code Integrity Error", shape=ellipse, fillcolor="#F44336", fontcolor="white"];
        Process [label="9. Process Payload", fillcolor="#E8F5E9"];
        Complete [label="10. Complete Transaction", shape=ellipse, fillcolor="#4CAF50", fontcolor="white"];
        
        Start -> CreateHash -> Sign -> Send;
        Send -> Receive;
        Receive -> VerifySig;
        VerifySig -> CheckPerm;
        CheckPerm -> QueryHash;
        QueryHash -> GetData;
        GetData -> Compare;
        Compare -> Invalid [label="Hash mismatch"];
        Compare -> Process [label="Hash match"];
        Process -> Complete;
    }

|

----

|

.. _stats:

=====
Stats
=====

|

.. raw:: html

    <div class="stats-row">
        <div class="stat-item">
            <h2>83%+</h2>
            <p>Test Coverage</p>
        </div>
        <div class="stat-item">
            <h2>300+</h2>
            <p>Unit Tests</p>
        </div>
        <div class="stat-item">
            <h2>15+</h2>
            <p>Modules</p>
        </div>
        <div class="stat-item">
            <h2>50+</h2>
            <p>Functions</p>
        </div>
    </div>

|

----

|

.. _use-cases:

=========
Use Cases
=========

.. grid:: 1 2 2 2
   :gutter: 3

   .. grid-item-card:: 🏥 Healthcare
      :text-align: center

      Secure patient data exchange between hospitals using Hyperledger Fabric with cryptographic identity verification.

   .. grid-item-card:: 🏦 Finance
      :text-align: center

      Implement regulatory compliance with tamper-proof transaction logs and audit trails.

   .. grid-item-card:: 🌐 Supply Chain
      :text-align: center

      Track products across supply chains with integrity-verified smart contracts.

   .. grid-item-card:: 🏛️ Government
      :text-align: center

      Zero Trust architecture for citizen services with fine-grained access control.

|

----

|

.. _documentation:

=============
Documentation
=============

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
   architecture
   glossary
   changelog
   bibliography

|

----

|

.. _additional-resources:

=====================
Additional Resources
=====================

|

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Resource
     - Link
   * - **PyPI Package**
     - https://pypi.org/project/wFabricSecurity/
   * - **GitHub Repository**
     - https://github.com/wisrovi/wFabricSecurity
   * - **Issue Tracker**
     - https://github.com/wisrovi/wFabricSecurity/issues
   * - **Hyperledger Fabric**
     - https://hyperledger-fabric.readthedocs.io/

|

----

|

.. _citation:

========
Citation
========

|

If you use wFabricSecurity in your research or project, please cite:

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

|

.. code-block:: text

   Rodriguez, W. (2026). wFabricSecurity: Zero Trust Security System 
   for Hyperledger Fabric. https://github.com/wisrovi/wFabricSecurity

|

----

|

.. _author:

======
Author
======

|

**William Rodriguez**

| Research Engineer & Software Architect
| eCaptured Technologies

| GitHub: https://github.com/wisrovi
| LinkedIn: https://es.linkedin.com/in/wisrovi-rodriguez
| Email: william.rodriguez@ecapturedtech.com

|

----

|

.. _license:

========
License
========

|

**MIT License**

| Copyright (c) 2026 William Rodriguez

|

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

|

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

|

**THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.**

|

----

|

*Last updated: |today|*
