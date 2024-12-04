.. include:: /includes/_links.rst

SNMP Library for Python |version|
=================================

.. toctree::
   :maxdepth: 1

   Return to PySNMP Homepage <https://pysnmp.com>

PySNMP is a cross-platform, pure-`Python`_ `SNMP`_
engine implementation. It features fully-functional SNMP engine capable
to act in Agent/Manager/Proxy roles, talking SNMP v1/v2c/v3 protocol
versions over IPv4/IPv6 and other network transports.

Despite its name, SNMP is not really a simple protocol. For instance its
third version introduces complex and open-ended security framework,
multilingual capabilities, remote configuration and other features.
PySNMP implementation closely follows intricate system details and features
bringing most possible power and flexibility to its users.

Current PySNMP stable version is |version|. It runs with Python 3.9+
and is recommended for new applications as well as for migration from
older, now obsolete, PySNMP releases.

Besides the libraries, a set of pure-Python `command line tools`_
are shipped along with the system. Those tools mimic the interface
and behavior of popular Net-SNMP snmpget/snmpset/snmpwalk utilities.
They may be useful in a cross-platform situations as well as a testing
and prototyping instrument for pysnmp users.

Quick Start and Samples
-----------------------

You already know something about SNMP and have no courage to dive into
this implementation? Try out quick start page!

We also have a collection of sample scripts to help you learn more about
every aspects of PySNMP.

.. toctree::
   :maxdepth: 1

   /quick-start
   /examples/index

Documentation
-------------

.. note::

   You can use version switch on the sidebar to browse documentation for
   other supported PySNMP versions.

.. warning::

   PySNMP 4.x, 5.x, and 6.0 are no longer supported. Materials about such
   deprecated versions have been removed, but can still be found in the
   `PySNMP GitHub repository`_.

   If you are using one of these versions, please consider upgrading to a
   supported version. You can find more information about supported
   versions and their lifecycle by visiting `this lifecycle page`_.

   You can learn more about how to upgrade from this page :doc:`/upgrade`.

Conceptual and API documentation are in the following section.

.. toctree::
   :maxdepth: 2

   /docs/index

.. note::

   Documentation about the SNMP protocol can be found on `PySNMP Homepage`_.

Troubleshooting
---------------

If you are having trouble with PySNMP, please check the following section
to learn troubleshooting tips, upgrade guides, and performance tuning
advice.

.. toctree::
   :maxdepth: 1

   /troubleshooting
   /upgrade
   /performance

Downloads
---------

Please study the following pages to learn how to download versions of our
PySNMP package, and what changes are included from their release notes.

.. toctree::
   :maxdepth: 1

   /download
   /changelog

License
-------

PySNMP software is free and open-source. Source code is hosted in
the `PySNMP Github repository`_.

The library is being distributed under 2-clause BSD-style license. More
details can be found in the following page.

.. toctree::
   :maxdepth: 1

   /license

PySNMP library development was initially sponsored by a `PSF`_ grant.

FAQ
---

We have a collection of frequently asked questions.

.. toctree::
   :maxdepth: 2

   /faq/index

Support
-------

To learn about community and commercial support options, please visit

.. toctree::
   :maxdepth: 1

   Support Options <https://www.pysnmp.com/support>

If you have other inquiries, please contact `LeXtudio Inc.`_.
