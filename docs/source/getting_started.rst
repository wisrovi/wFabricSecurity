.. _getting_started:

=============
Getting Started
=============

Get up and running with wFabricSecurity in minutes.

|

.. contents::
   :local:
   :depth: 3

|

|

----

|

.. _getting-started-prerequisites:

==============
Prerequisites
==============

|

Before installing wFabricSecurity, ensure you have:

|

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Requirement
     - Description
   * - **Python**
     - Version 3.10 or higher
   * - **pip**
     - Latest version recommended
   * - **Operating System**
     - Linux, macOS, or Windows

|

Verify your Python installation:

|

.. code-block:: bash

   python --version
   # Should show: Python 3.10.x or higher

   pip --version
   # Should show: pip 22.x or higher

|

|

----

|

.. _getting-started-installation:

============
Installation
============

|

The recommended way to install wFabricSecurity is via pip:

|

.. code-block:: bash

   pip install wFabricSecurity

|

For development or to install from source:

|

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/wisrovi/wFabricSecurity.git
   cd wFabricSecurity

   # Install in development mode
   pip install -e .

   # Or install with dev dependencies
   pip install -e ".[dev]"

|

|

|

.. _getting-started-verification:

============
Verification
============

|

Verify the installation was successful:

|

.. code-block:: python

   import wFabricSecurity

   print(f"wFabricSecurity version: {wFabricSecurity.__version__}")

|

Or run a quick test:

|

.. code-block:: bash

   python -c "from wFabricSecurity import FabricSecurity; print('✓ Installation successful!')"

|

|

----

|

.. _getting-started-quick-start:

============

Quick Start
============

|

Get started with wFabricSecurity in three simple steps:

|

.. _step-1:

Step 1: Basic Initialization
---------------------------

|

.. code-block:: python

   from wFabricSecurity import FabricSecuritySimple

   # Initialize the security system
   security = FabricSecuritySimple(
       msp_path="/path/to/your/msp"
   )

   print("✓ Security system initialized!")

|

|

.. _step-2:

Step 2: Verify a Message
------------------------

|

.. code-block:: python

   from wFabricSecurity import FabricSecuritySimple

   security = FabricSecuritySimple(msp_path="/path/to/msp")

   # Verify an incoming message
   result = security.verify_and_process(
       payload='{"action": "process_data", "id": "12345"}',
       sender="CN=Master"
   )

   if result:
       print("✓ Message verified and processed!")
   else:
       print("✗ Verification failed!")

|

|

.. _step-3:

Step 3: Create Secure Communication
-----------------------------------

|

.. code-block:: python

   from wFabricSecurity import FabricSecurity
   from wFabricSecurity.fabric_security.core.enums import CommunicationDirection

   # Full initialization
   security = FabricSecurity(
       me="Master",
       msp_path="/path/to/msp"
   )

   # Register identity
   security.register_identity()

   # Define communication permissions
   security.register_communication(
       from_participant="CN=Master",
       to_participant="CN=Slave",
       direction=CommunicationDirection.BIDIRECTIONAL
   )

   # Create a signed message
   message = security.create_message(
       recipient="CN=Slave",
       content='{"operation": "process_data"}'
   )

   print(f"✓ Message created: {message}")

|

|

----

|

.. _getting-started-complete-example:

==================
Complete Example
==================

|

A full working example:

|

.. code-block:: python

   """
   wFabricSecurity Quick Start Example
   Complete demonstration of Zero Trust security features.
   """

   from wFabricSecurity import FabricSecurity
   from wFabricSecurity.fabric_security.core.enums import CommunicationDirection
   from wFabricSecurity.fabric_security.core.exceptions import (
       CodeIntegrityError,
       PermissionDeniedError
   )

   def main():
       # Initialize security system
       security = FabricSecurity(
           me="Master",
           msp_path="/path/to/msp"
       )

       # 1. Register identity
       print("1. Registering identity...")
       security.register_identity()
       print(f"   ✓ Identity registered: {security.me}")

       # 2. Register code integrity
       print("2. Registering code integrity...")
       security.register_code(
           files=["main.py", "utils.py"],
           version="1.0.0"
       )
       print("   ✓ Code integrity registered")

       # 3. Set up communication permissions
       print("3. Configuring permissions...")
       security.register_communication(
           "CN=Master",
           "CN=Slave",
           CommunicationDirection.BIDIRECTIONAL
       )
       print("   ✓ Communication permissions configured")

       # 4. Create and send a message
       print("4. Creating signed message...")
       message = security.create_message(
           recipient="CN=Slave",
           content='{"operation": "process_data", "payload": "test"}'
       )
       print(f"   ✓ Message created: {message.sender} -> {message.recipient}")

       # 5. Verify the message
       print("5. Verifying message...")
       if security.verify_message(message):
           print("   ✓ Message verified successfully!")
       else:
           print("   ✗ Verification failed!")

       print("\n" + "="*50)
       print("✓ All operations completed successfully!")
       print("="*50)

   if __name__ == "__main__":
       main()

|

|

----

|

.. _getting-started-next-steps:

============

Next Steps
============

|

Now that you have wFabricSecurity installed, explore these resources:

|

.. grid:: 1 2 2 2
   :gutter: 3

   .. grid-item-card:: 📖 Tutorials
      :text-align: center

      Step-by-step guides for common use cases.

      +++
      See :ref:`tutorials`

   .. grid-item-card:: 📚 API Reference
      :text-align: center

      Complete documentation of all classes and methods.

      +++
      See :ref:`api_reference`

   .. grid-item-card:: 🏗️ Architecture
      :text-align: center

      System architecture and design patterns.

      +++
      See :ref:`architecture`

   .. grid-item-card:: ❓ FAQ
      :text-align: center

      Answers to common questions.

      +++
      See :ref:`faq`

|

|

----

|

.. seealso::

   * :ref:`installation` - Detailed installation instructions
   * :ref:`usage` - Usage examples and patterns
   * :ref:`tutorials` - Step-by-step tutorials
