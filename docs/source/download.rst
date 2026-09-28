.. include:: /includes/_links.rst

Downloads
=========

.. toctree::
   :maxdepth: 2

The PySNMP software is provided under terms and conditions of BSD-style
license, and can be freely downloaded from `PySNMP PyPI package`_.

The best way to obtain PySNMP from PyPI is to run:

.. code-block:: bash

   $ pip install pysnmp

This Python package has the following dependencies:

* ``pyasn1`` package from PyASN1
* If ``pysmi`` package (2.0.0 and above) from PySMI presents, MIB services
  are enabled.
* If ``cryptography`` package presents, strong SNMPv3 encryption is enabled.

.. note::

   If you want to try the cutting-edge development code then it could be
   taken from development branches in `PySNMP GitHub repository`_. It may
   be less stable in regards to general operation and changes to public
   interfaces, but it's first to contain fixes to recently discovered bugs.


Related Resources
-----------------

- `Support Options`_
- :doc:`/quick-start`
- :doc:`/troubleshooting`
- :doc:`/faq/index`
- :doc:`/changelog`
