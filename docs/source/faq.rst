.. _faq:

===
FAQ
===

Frequently Asked Questions about wFabricSecurity.

|

.. contents::
   :local:
   :depth: 3

|

----

|

.. _faq-general:

==========
General
==========

|

.. dropdown:: What is wFabricSecurity?

   wFabricSecurity is a **Zero Trust Security System** for Hyperledger Fabric that provides:

   * Cryptographic identity verification
   * Code integrity validation
   * Secure message signing and verification
   * Communication permission management
   * Rate limiting for DoS protection
   * Certificate caching for performance

|

.. dropdown:: What is Zero Trust?

   **Zero Trust** is a security model that operates on the principle: **"Never trust, always verify."**

   In Zero Trust:

   * No participant is automatically trusted
   * Every request must be authenticated
   * Every transaction must be authorized
   * Continuous verification is required
   * Least privilege access is enforced

   wFabricSecurity implements Zero Trust by verifying:

   * Identity via X.509 certificates
   * Code integrity via SHA-256 hashes
   * Message authenticity via ECDSA signatures
   * Permissions via access control lists

|

.. dropdown:: Why use wFabricSecurity?

   wFabricSecurity is ideal for:

   | **Healthcare**: Secure patient data exchange
   | **Finance**: Regulatory compliance and audit trails
   | **Supply Chain**: Product tracking with integrity verification
   | **Government**: Zero Trust architecture for citizen services
   | **IoT**: Device authentication and secure communication

|

.. dropdown:: What are the system requirements?

   | **Python**: 3.10 or higher
   | **OS**: Linux, macOS, Windows
   | **RAM**: Minimum 2GB
   | **Storage**: 100MB for package, plus MSP credentials
   | **Network**: Access to Hyperledger Fabric peers (if using Fabric integration)

|

----

|

.. _faq-installation:

============
Installation
============

|

.. dropdown:: How do I install wFabricSecurity?

   Install via pip:

   .. code-block:: bash

      pip install wFabricSecurity

   Or from source:

   .. code-block:: bash

      git clone https://github.com/wisrovi/wFabricSecurity.git
      cd wFabricSecurity
      pip install -e .

|

.. dropdown:: What are the dependencies?

   **Core Dependencies:**

   * ``cryptography`` - For ECDSA signing and X.509 certificates
   * ``ecdsa`` - Elliptic curve cryptography
   * ``requests`` - HTTP client for Fabric gateway

   **Optional Dependencies:**

   * ``hyperledger-fabric-gateway`` - For Fabric integration
   * ``sphinx`` - For documentation building

|

.. dropdown:: How do I verify the installation?

   .. code-block:: python

      from wFabricSecurity import FabricSecurity

      # Test basic import
      print(f"Version: {FabricSecurity.__module__}")

      # Run self-test
      from wFabricSecurity.fabric_security.security.integrity import IntegrityVerifier
      verifier = IntegrityVerifier()
      print("✓ Installation verified!")

|

----

|

.. _faq-security:

============
Security
============

|

.. dropdown:: How does code integrity verification work?

   | **Step 1**: Compute SHA-256 hash of source files
   | **Step 2**: Sign the hash with ECDSA private key
   | **Step 3**: Store signed hash on Fabric ledger
   | **Step 4**: At runtime, recompute hash and compare

   If hashes don't match, code tampering is detected.

|

.. dropdown:: What hashing algorithm is used?

   **SHA-256 (Secure Hash Algorithm 256-bit)**

   * Part of the SHA-2 family
   * Produces 256-bit (32-byte) hash
   * No known collision attacks
   * Used for code integrity and message integrity

|

.. dropdown:: What signing algorithm is used?

   **ECDSA (Elliptic Curve Digital Signature Algorithm)**

   * Curve: secp256k1
   * Key size: 256 bits
   * Signature size: 64 bytes
   * Same algorithm as Bitcoin

|

.. dropdown:: How are private keys protected?

   wFabricSecurity never stores private keys directly. Instead:

   | **1.** Keys remain in your MSP directory
   | **2.** Cryptographic operations use OS key stores
   | **3.** Keys are referenced by path, not loaded into memory
   | **4.** Hardware Security Modules (HSM) are supported

|

.. dropdown:: Can wFabricSecurity prevent all attacks?

   wFabricSecurity provides strong security guarantees for:

   | ✓ Code tampering detection
   | ✓ Message authenticity
   | ✓ Identity verification
   | ✓ Permission enforcement
   | ✓ Rate limiting

   However, security is a chain - it's only as strong as the weakest link:

   | ✗ Cannot protect against compromised private keys
   | ✗ Cannot prevent physical security breaches
   | ✗ Cannot fix application-level vulnerabilities

|

----

|

.. _faq-fabric:

============
Hyperledger Fabric
============

|

.. dropdown:: What Fabric versions are supported?

   | **Hyperledger Fabric**: 2.x, 3.x
   | **Gateway API**: 1.0+

|

.. dropdown:: Do I need a Fabric network to use wFabricSecurity?

   **No**, wFabricSecurity works in two modes:

   | **Standalone Mode**: Use LocalStorage instead of Fabric
   | **Fabric Mode**: Full integration with Fabric ledger

   Standalone mode is useful for:

   * Development and testing
   * Offline scenarios
   * Gradual Fabric adoption

|

.. dropdown:: How do I configure the Fabric gateway?

   .. code-block:: python

      from wFabricSecurity import FabricSecurity

      security = FabricSecurity(
          me="ParticipantName",
          msp_path="/path/to/msp",
          gateway_path="/path/to/connection-profile.yaml"
      )

   The gateway connection profile can be:

   * A file path (``.yaml`` or ``.json``)
   * A dictionary with connection details
   * Environment variable reference

|

.. dropdown:: What happens if Fabric is unavailable?

   wFabricSecurity handles Fabric unavailability gracefully:

   | **1.** Falls back to LocalStorage for non-critical data
   | **2.** Queues Fabric operations for retry
   | **3.** Raises appropriate exceptions for critical failures
   | **4.** Logs warnings for degraded operation

|

----

|

.. _faq-performance:

============
Performance
============

|

.. dropdown:: How fast is signature verification?

   | **ECDSA Sign**: ~1-2ms per operation
   | **ECDSA Verify**: ~2-3ms per operation
   | **SHA-256 Hash**: ~0.1ms per MB

   These are typical benchmarks on modern hardware.

|

.. dropdown:: Does certificate caching help?

   **Yes**, significantly!

   | **Without cache**: ~10-50ms (disk I/O + parsing)
   | **With cache**: ~0.1ms (memory lookup)

   Default configuration:

   .. code-block:: python

      identity = IdentityManager(
          cache_size=1024,  # 1024 certificates
          ttl=3600          # 1 hour TTL
      )

|

.. dropdown:: How do I tune performance?

   **For High Throughput:**

   .. code-block:: python

      security = FabricSecurity(
          # Increase cache size
          certificate_cache_size=4096,
          certificate_ttl=7200,  # 2 hours

          # Reduce logging
          log_level=logging.WARNING
      )

   **For Development:**

   .. code-block:: python

      security = FabricSecurity(
          # Use local storage instead of Fabric
          use_local_storage=True,

          # Smaller cache
          certificate_cache_size=128
      )

|

----

|

.. _faq-troubleshooting:

============
Troubleshooting
============

|

.. dropdown:: I'm getting "Permission Denied" errors

   | **Check 1**: Are permissions registered?

   .. code-block:: python

      security.register_communication(
          from_participant="CN=Master",
          to_participant="CN=Slave",
          direction=CommunicationDirection.BIDIRECTIONAL
      )

   | **Check 2**: Is the direction correct?

   .. code-block:: python

      # Master can send to Slave
      security.register_communication(
          "CN=Master", "CN=Slave",
          CommunicationDirection.OUTBOUND  # Master sends
      )

      # For bidirectional
      security.register_communication(
          "CN=Slave", "CN=Master",
          CommunicationDirection.OUTBOUND  # Slave sends back
      )

   | **Check 3**: Check current permissions

   .. code-block:: python

      print(security.get_permission_matrix())

|

.. dropdown:: Code integrity check is failing

   | **Possible Causes**:

   | 1. Source files were modified after registration
   | 2. Hash stored on ledger doesn't match current code
   | 3. Different file versions in different environments

   | **Solutions**:

   | 1. Re-register code after updates

   .. code-block:: python

      security.register_code(
          files=["updated.py"],
          version="1.1.0",
          store_on_ledger=True
      )

   | 2. Temporarily disable verification (development only)

   .. code-block:: python

      security = FabricSecurity(
          me="Dev",
          msp_path="/path/to/msp",
          skip_code_verification=True  # Only for development!
      )

|

.. dropdown:: Rate limiting is too restrictive

   Adjust the rate limiter configuration:

   .. code-block:: python

      security = FabricSecurity(
          me="Master",
          msp_path="/path/to/msp",
          rate_limit=100,       # 100 requests/second
          rate_capacity=500      # Burst of 500
      )

   Or per-participant:

   .. code-block:: python

      security.configure_rate_limit(
          participant="CN=TrustedPartner",
          rate=1000,     # Higher limit
          capacity=5000  # Larger burst
      )

|

.. dropdown:: Can't connect to Fabric gateway

   | **Check 1**: Gateway file exists and is readable

   .. code-block:: bash

      ls -la /path/to/connection-profile.yaml

   | **Check 2**: Identity exists in wallet

   .. code-block:: python

      # Check gateway connectivity
      from wFabricSecurity.fabric_security.fabric.gateway import FabricGateway
      gw = FabricGateway(gateway_path="/path/to/profile")
      gw.connect()  # Will raise if invalid

   | **Check 3**: Network connectivity to peers

   .. code-block:: bash

      telnet peer0.org1.example.com 7051

|

.. dropdown:: Certificate parsing errors

   | **Check 1**: Valid X.509 certificate format

   .. code-block:: bash

      # Should show certificate info
      openssl x509 -in /path/to/cert.pem -text -noout

   | **Check 2**: Correct MSP structure

   .. code-block:: text

      msp/
      ├── cacerts/
      ├── signcerts/
      └── keystore/

   | **Check 3**: Update cryptography package

   .. code-block:: bash

      pip install --upgrade cryptography

|

----

|

.. _faq-development:

============
Development
============

|

.. dropdown:: How do I contribute to wFabricSecurity?

   | **1.** Fork the repository
   | **2.** Create a feature branch

   .. code-block:: bash

      git checkout -b feature/your-feature

   | **3.** Make your changes
   | **4.** Add tests

   .. code-block:: bash

      pytest test/ -v

   | **5.** Submit a pull request

|

.. dropdown:: How do I run the tests?

   .. code-block:: bash

      # Install dev dependencies
      pip install -e ".[dev]"

      # Run all tests
      pytest test/ -v

      # Run with coverage
      pytest test/ --cov=wFabricSecurity --cov-report=html

      # Run specific test file
      pytest test/test_crypto.py -v

|

.. dropdown:: How do I build the documentation?

   .. code-block:: bash

      # Install documentation dependencies
      pip install -r docs/requirements.txt

      # Build HTML docs
      cd docs
      make html

      # View locally
      open _build/html/index.html

|

----

|

.. _faq-licensing:

============
Licensing
============

|

.. dropdown:: What license does wFabricSecurity use?

   **MIT License**

   You can:

   | ✓ Use in commercial projects
   | ✓ Modify the code
   | ✓ Distribute
   | ✓ Use privately

   You must:

   | ✓ Include the copyright notice
   | ✓ Include the license text

|

.. dropdown:: Can I use wFabricSecurity in commercial products?

   **Yes**, wFabricSecurity is MIT licensed, which is a permissive license that allows commercial use.

   See the `LICENSE <https://github.com/wisrovi/wFabricSecurity/blob/main/LICENSE>`_ file for details.

|

----

|

.. _faq-support:

============
Support
============

|

.. dropdown:: Where can I get help?

   | **Documentation**: You're already here! 📚
   | **GitHub Issues**: https://github.com/wisrovi/wFabricSecurity/issues
   | **Email**: william.rodriguez@ecapturedtech.com

|

.. dropdown:: How do I report bugs?

   | **1.** Check existing issues to avoid duplicates
   | **2.** Create a new issue with:

   .. code-block:: text

      ## Bug Description
      [Clear description of the bug]

      ## Steps to Reproduce
      1. [Step 1]
      2. [Step 2]
      3. [Step 3]

      ## Expected vs Actual Behavior
      [What you expected]
      [What actually happened]

      ## Environment
      - OS: [Your OS]
      - Python: [Version]
      - wFabricSecurity: [Version]

|

.. dropdown:: Is there a community or chat?

   | **GitHub Discussions**: https://github.com/wisrovi/wFabricSecurity/discussions
   | **LinkedIn**: https://es.linkedin.com/in/wisrovi-rodriguez

|

|

.. seealso::

   * :ref:`api_reference` - Complete API documentation
   * :ref:`tutorials` - Step-by-step implementation guides
   * :ref:`architecture` - System architecture details
   * :ref:`glossary` - Terms and definitions
