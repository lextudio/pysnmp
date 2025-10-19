.. include:: /includes/_links.rst

Asynchronous SNMP (v3arch)
==========================

Python 3.4 introduced a new module - `asyncio` (former Tulip,
PEP 3156) featuring infrastructure for writing single-threaded concurrent
code using coroutines, multiplexing I/O access over sockets and other
resources.

PySNMP library was originally built on top of Python's asynchronous I/O
library called asyncio. The asyncio module offers similar functionality
but uses much more modern and powerful language facilities. Functionally,
asyncio can replace asyncio in PySNMP however its use requires understanding
the concepts such as coroutines and generators. If your task is to embed SNMP
stack into an existing asyncio-based app, using PySNMP's asyncio interfaces
greatly simplifies the task.

All SNMP-related functionality of Native PySNMP API to Standard SNMP
Applications (`RFC3413`_)
remains available to asyncio-backed applications.

We do not provide Command Generator and Notification Originator examples,
as it is much easier to use
:doc:`high-level interfaces </examples/hlapi/v3arch/asyncio/index>` instead.

Command Responder Applications
------------------------------

.. toctree::

   /examples/v3arch/asyncio/agent/cmdrsp/agent-side-mib-implementations
   /examples/v3arch/asyncio/agent/cmdrsp/snmp-versions

Notification Receiver Applications
----------------------------------

.. toctree::

   /examples/v3arch/asyncio/manager/ntfrcv/transport-tweaks

For more details on PySNMP programming model and interfaces, please
refer to the documentation
