.. include:: /includes/_links.rst

Samples
=======

.. toctree::
   :maxdepth: 2

SNMP is not simple (PySNMP implementation takes over 15K lines of
Python code), but PySNMP tries to hide the complexities and let you
carry out typical SNMP operations in a quick and intuitive way.

PySNMP offers high and low-level programming interfaces to deal with
SNMP protocol.

The other dimension of differences in the PySNMP APIs is that there are
two different SNMP implementations - the initial architecture
(`RFC1901 <https://tools.ietf.org/html/rfc1901>`_ ..
`RFC1905 <https://tools.ietf.org/html/rfc1905>`_) also known as SNMP v1 architecture
and the redesigned variant (`RFC3413 <https://tools.ietf.org/html/rfc3413>`_
and others) -- SNMPv3 architecture.

.. note::

   The SNMP v1 architecture supports SNMP protocol versions 1 and 2c,
   while SNMP v3 architecture supports versions 1, 2c and 3. Whatever
   new amendments to the SNMP protocol may come up in the future, they
   will be implemented within the v3 model.

High-Level API
--------------

The high-level API (`hlapi`) is designed to be simple, concise and
suitable for the most typical client-side operations. For that matter,
only Command Generator and Notification Originator Applications are
wrapped into a nearly one-line Python expression.

The `hlapi` interfaces come in several flavours: one synchronous
and a bunch of asynchronous, adapted to work withing the event loops
of popular asynchronous I/O frameworks.

The primary reason for maintaining high-level API over both `v1arch` and
`v3arch` is performance - `v3arch` machinery is much more functional and complicated
internally, that translates to being heavier on resources and therefore slower.

The v3 architecture
+++++++++++++++++++

.. toctree::
   :maxdepth: 2

   /examples/hlapi/asyncio/index


The v1 architecture
+++++++++++++++++++

.. toctree::
   :maxdepth: 2

   /examples/hlapi/v1arch/asyncore/sync/contents

.. toctree::
   :maxdepth: 2

   /examples/hlapi/v1arch/asyncore/contents

.. toctree::
   :maxdepth: 2

   /examples/hlapi/v1arch/asyncio/contents

Low-level v3 architecture
-------------------------

Complete implementation of all official Standard SNMP Applications. It
should let you implement any SNMP operation defined in the standard
at the cost of working at a somewhat low level.

This API also used to come in several transport varieties depending on I/O
framework being used. But now only asyncio based API is supported.

.. toctree::
   :maxdepth: 2

   /examples/v3arch/asyncio/index

.. note::

   It is recommended that you move away from other APIs such as asyncore
   based ones, as they are not maintained and will be removed in future.

Packet Level SNMP
-----------------

In cases where performance is your top priority and you only need to
work with SNMP v1 and v2c systems and you do not mind writing much
more code, then there is a low-level API to SNMP v1/v2c PDU and
PySNMP I/O engine. There's practically no SNMP engine or SMI
infrastructure involved in the operations of these almost wire-level
interfaces. Although MIB services can still be used separately.

A packet-level API-based application typically manages both SNMP
message building/parsing and network communication via one or more
transports. It's fully up to the application to handle failures on
message and transport levels.

Command Generator
+++++++++++++++++

If you are developing an SNMP manager application, you will most likely
want to study the following examples and learn how to send out SNMP
requests.

.. toctree::

   /examples/v1arch/asyncio/manager/cmdgen/fetching-variables
   /examples/v1arch/asyncio/manager/cmdgen/modifying-variables
   /examples/v1arch/asyncio/manager/cmdgen/walking-operations
   /examples/v1arch/asyncio/manager/cmdgen/transport-tweaks

Command Responder
+++++++++++++++++

If you are developing an SNMP agent application, you will most likely want
to study the following examples and learn how to respond to SNMP requests.

.. toctree::

   /examples/v1arch/asyncio/agent/cmdrsp/agent-side-mib-implementations

Notification Originator
+++++++++++++++++++++++

These examples demonstrate how to send SNMP notifications, usually from an
SNMP agent application.

.. toctree::

   /examples/v1arch/asyncio/agent/ntforg/transport-tweaks

Notification Receiver
+++++++++++++++++++++

These examples demonstrate how to receive SNMP notifications, usually in an
SNMP manager application.

.. toctree::

   /examples/v1arch/asyncio/manager/ntfrcv/transport-tweaks

Low Level MIB Access
--------------------

Accessing MIB objects is a common task in SNMP applications, so the
following examples demonstrate how to do that.

.. toctree::

   /examples/smi/manager/browsing-mib-tree
   /examples/smi/agent/implementing-mib-objects

Using these examples
--------------------

.. note::

   It is difficult to cover all examples on this site, so you might want to
   visit the ``examples`` folder in `PySNMP GitHub repository`_.

Before using the sample code, make sure ``pysnmp-lextudio`` and its
dependencies are installed. You might refer to :doc:`/quick-start` for
details.

Many sample scripts use the public, multilingual SNMP Command Responder and
Notification Receiver configured at `demo.pysnmp.com`_, which enable you to
run them in a cut&paste fashion.

If you wish to use your own SNMP Agent with these scripts, make sure to
either configure your local snmpd and/or snmptrapd, or use a valid address
and SNMP credentials of your SNMP Agent in the examples to let them work.

Should you want to use a MIB to make SNMP operations more human-friendly,
you are welcome to search for it and possibly download one from our
public MIB repository `mibs.pysnmp.com`_. Alternatively,
you can configure PySNMP to fetch and cache required MIBs from there
automatically.

Related Resources
-----------------

- :doc:`/quick-start`
- :doc:`/troubleshooting`
- :doc:`/docs/api-reference`
