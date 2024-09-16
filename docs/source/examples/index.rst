.. include:: /includes/_links.rst

Samples
=======

.. warning::

   Many of the examples were written a few years ago by the previous
   maintainers of PySNMP. They might still be valid and useful, but they
   might also be outdated and not reflect the best practices.

   The most reliable resources to see the API in action are the unit test
   cases under the ``tests`` folder in the `PySNMP GitHub repository`_.

   If you find any issues with the examples, please report them to the
   current PySNMP maintainers.

   Visit `Support Options`_ for more information.

.. toctree::
   :maxdepth: 2

SNMP is not simple (PySNMP implementation takes over 15K lines of
Python code), but PySNMP tries to hide the complexities and let you
carry out typical SNMP operations in a quick and intuitive way.

PySNMP offers three groups of programming interfaces to deal with
SNMP protocol. In the order from most concise to most detailed those
APIs follow.

High-Level API
--------------

The so-called high-level API (hlapi) is designed to be simple, concise and
suitable for the most frequent operations. For that matter only
Command Generator and Notification Originator Applications are currently
wrapped into a nearly one-line Python expression.

It used to come in many flavours: one synchronous and a bunch of bindings
to popular asynchronous I/O frameworks. Those varieties of APIs bring
subtile differences, mostly to better match particular I/O framework
customs. But now only asyncio based API is supported.

.. toctree::
   :maxdepth: 2

   /examples/hlapi/asyncio/index

Unless you have a very specific task, the high-level API might
solve your SNMP needs.

.. note::

   It is recommended that you move away from other APIs such as asyncore
   based ones, as they are not maintained and will be removed in future.

Native SNMP API
---------------

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

Before using the sample code, make sure ``pysnmp`` and its
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
