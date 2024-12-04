.. include:: /includes/_links.rst

Performance Tuning
==================

PySNMP is a highly optimized software. However, there are some knobs you
can turn to make it work even faster. Here are some tips:

Disabling MIB Support
---------------------

Loading MIB metadata into memory is a costly operation. If you are not
using MIBs in your application, you can disable MIB support by

TODO: Add a code snippet here.

Run Python Release Mode
-----------------------

Python interpreter can run in debug and release modes. Running in release
mode can make your Python code run faster. To run Python in release mode,
you can use the following command:

.. code-block:: bash

   $ python -O myscript.py

Choosing the Right High-Level API
---------------------------------

PySNMP comes with two high-level APIs: v1 and v3.

If you are using SNMPv1 and SNMPv2c, and you are not using any security
features in your application, you should use the v1 API. The
``SnmpDispatcher`` based API is the fastest API in PySNMP, as it simply
sends SNMP packets and does not do any heavy processing on the packets.

If you are using SNMPv3, you have to use the v3 API with USM and VACM to
handle security and access control. The v3 API is significantly slower than
the v1 API because it builds up a local secure engine and has to do more
processing on the packets in order to be compliant with SNMPv3 standards.

Using the right API, and using the right features in the API can make your
application run reasonably fast.

Don't trust blindly other Python SNMP libraries claiming to be faster. They
either lack of essential features that make the comparison pointless or
they bind to native libraries that become your nightmare to maintain and
deploy. In the end the performance is limited by the Python interpreter and
the SNMP protocol itself.
