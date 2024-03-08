.. include:: /includes/_links.rst

SNMP Library for Python 6.0
===========================

.. toctree::
   :maxdepth: 2

PySNMP is a cross-platform, pure-`Python`_ `SNMP`_
engine implementation. It features fully-functional SNMP engine capable
to act in Agent/Manager/Proxy roles, talking SNMP v1/v2c/v3 protocol
versions over IPv4/IPv6 and other network transports.

Despite its name, SNMP is not really a simple protocol. For instance its
third version introduces complex and open-ended security framework,
multilingual capabilities, remote configuration and other features.
PySNMP implementation closely follows intricate system details and features
bringing most possible power and flexibility to its users.

Current PySNMP stable version is 6.0. It runs with Python 3.8+
and is recommended for new applications as well as for migration from
older, now obsolete, PySNMP releases. All site documentation and
examples are written for the 6.0 and later versions in mind.
Older materials have been removed.

Besides the libraries, a set of pure-Python `command line tools`_
are shipped along with the system. Those tools mimic the interface
and behavior of popular Net-SNMP snmpget/snmpset/snmpwalk utilities.
They may be useful in a cross-platform situations as well as a testing
and prototyping instrument for pysnmp users.

PySNMP software is free and open-source. Source code is hosted in
the `PySNMP Github repository`_.
The library is being distributed under 2-clause BSD-style license.

PySNMP library development has been initially sponsored
by a `PSF`_ grant.

Quick Start
-----------

You already know something about SNMP and have no courage to dive into
this implementation? Try out quick start page!

.. toctree::
   :maxdepth: 1

   Return to PySNMP Homepage <https://pysnmp.com>
   /quick-start

Documentation
-------------

You can find conceptual and API documentation in the following section.

.. toctree::
   :maxdepth: 2

   /docs/index

Samples
-------

We have a collection of sample scripts to help you get started with PySNMP.

.. toctree::
   :maxdepth: 2

   /examples/index

Troubleshooting
---------------

If you are having trouble with PySNMP, please check the following section.

.. toctree::
   :maxdepth: 1

   /troubleshooting
   /upgrade

Downloads
---------

Best way is usually to install PySNMP using `PySNMP PyPI package`_.

.. code-block:: bash

   $ pip install pysnmp-lextudio

If that does not work for you for some reason, you might need to read the
following page.

.. toctree::
   :maxdepth: 1

   /download

License
-------

This library is distributed under 2-clause BSD-style license.

.. toctree::
   :maxdepth: 1

   /license

FAQ
---

We have a collection of frequently asked questions.

.. toctree::
   :maxdepth: 2

   /faq

Further Development
-------------------

We fanatically document all fixes, changes and new features in changelog.

.. toctree::
   :maxdepth: 1

   /changelog

Contact
-------

In case of questions or troubles using PySNMP, please open up a
new `GitHub issue`_ or ask on `Stack Overflow`_.

For other inquiries, please contact `LeXtudio Inc.`_.

More information about support options can be found in the following
section.

.. toctree::
   :maxdepth: 1

   Support Options <https://www.pysnmp.com/support>
