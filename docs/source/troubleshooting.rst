.. include:: /includes/_links.rst

Troubleshooting
===============

.. toctree::
   :maxdepth: 2

If you find your PySNMP application behaving unexpectedly, try to enable
a /more or less verbose/ built-in PySNMP debugging by adding the
following snippet of code at the beginning of your application:

.. code-block:: python

    from pysnmp import debug

    # use specific flags or 'all' for full debugging
    debug.setLogger(debug.Debug('dsp', 'msgproc', 'secmod'))

Then run your app and watch stderr. The Debug initializer enables debugging
for a particular PySNMP subsystem, 'all' enables full debugging. More
specific flags are:

* io
* dsp
* msgproc
* secmod
* mibbuild
* mibview
* mibinstrum
* acl
* proxy
* app

You might refer to PySNMP source code to see in which components these
flags are used.

References
----------

- :doc:`/quick-start`
- :doc:`/examples/index`
- :doc:`/docs/api-reference`
