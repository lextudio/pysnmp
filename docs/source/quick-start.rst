.. include:: /includes/_links.rst

Quick Start
===========

.. toctree::
   :maxdepth: 2

Once you decide to test out PySNMP library on your Linux/Windows/macOS
system, you should start to prepare a test field folder and configure the
Python environment.

Set Up Test Field Folder
------------------------
First, it is recommended that you use `pyenv`_ to manage different Python
versions on this machine. If you are using Windows, you can use `pyenv-win`_.

Next, we assume you are now on macOS/Linux, and the following commands
initialize a folder for us,

.. code-block:: bash

   $ cd ~
   $ mkdir test-field
   $ cd test-field
   $ pyenv local 3.12
   $ pip install pipenv
   $ pipenv install pysnmp
   $ pipenv run pip list

Here we created a virtual environment using ``pipenv`` for this folder, and
installed ``pysnmp`` so that you can move on with the following
sections.

The final command should print out the dependencies and you should be able to
see ``pysnmp`` version 6.0+ there.

.. note::

   If you haven't installed Python 3.12 with ``pyenv``, you should execute
   ``pyenv install 3.12``.

   To delete the virtual environment for this folder, you can use

   .. code-block:: bash

      $ pipenv --rm

   It is common that you use another virtual environment tool, such as venv,
   poetry, or conda. Just make sure you use the equivalent commands to set up the
   virtual environment for testing.

   It is highly recommended that you use a Python virtual environment, as it
   makes dependency management and troubleshooting much easier.

Fetch SNMP Variable
-------------------

Next, let's write some test script and play with PySNMP manager side operations.

#. Create a Python script in the test field folder, such as ``v1-get.py``.
#. Cut and paste the following contents below into this file,

   .. literalinclude:: /../../examples/hlapi/v3arch/asyncio/manager/cmdgen/v1-get.py
      :start-after: """  #
      :language: python

   :download:`Download</../../examples/hlapi/v3arch/asyncio/manager/cmdgen/v1-get.py>` script.

#. Execute this script. If everything works as it should you will get the following on your
   console:

   .. code-block:: bash

      $ pipenv run python v1-get.py
      ...
      SNMPv2-MIB::sysDescr."0" = SunOS zeus.pysnmp.com 4.1.3_U1 1 sun4m
      >>>

Here you can see SNMP v1 GET operation can be easily done with the
:py:class:`~pysnmp.hlapi.v3arch.asyncio.slim` class. Other operations in SNMP v1
and v2c can be done in similar manner. To execute SNMP v3 operations,
however, requires more complex code.

The test agent we use is hosted at `demo.pysnmp.com`_.

Send SNMP TRAP
--------------

Similarly we can perform agent side operations with PySNMP.

#. Create a script file ``default-v1-trap.py``.
#. Cut and paste the following contents below into this file,

   .. literalinclude:: /../../examples/hlapi/v3arch/asyncio/agent/ntforg/default-v1-trap.py
      :start-after: """  #
      :language: python

   :download:`Download</../../examples/hlapi/v3arch/asyncio/agent/ntforg/default-v1-trap.py>` script.

#. Execute this script.

   .. code-block:: bash

      $ pipenv run python default-v1-trap.py

Because this sends out an SNMP v1 TRAP message, we know that no response will be
received.

The notification receiver the receives this message is hosted at
`demo.pysnmp.com`_.

Related Resources
-----------------

- `Support Options`_
- :doc:`/examples/index`
- :doc:`/troubleshooting`
- :doc:`/docs/api-reference`
