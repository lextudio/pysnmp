.. include:: /includes/_links.rst

Troubleshooting
===============

.. toctree::
   :maxdepth: 2

Don't panic when your PySNMP application does not work as expected. This
page provides some tips and tricks to troubleshoot your PySNMP application.

PySNMP Built-in Debugging
-------------------------

If you find your PySNMP application behaving unexpectedly, try to enable
a /more or less verbose/ built-in PySNMP debugging by adding the
following snippet of code at the beginning of your application:

.. code-block:: python

    from pysnmp import debug

    # use specific flags for debugging
    debug.setLogger(debug.Debug('dsp', 'msgproc', 'secmod'))

    # use 'all' for full debugging
    debug.setLogger(debug.Debug('all'))

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

Common Utilities
----------------

While built-in debugging is a good start, you might want to use some other
tools and utilities to troubleshoot your PySNMP application at packet level
so as to gain more insights. Then you might want to use some tools below,

- `Wireshark`_ is a great tool to see what's going on the wire.
- `tcpdump`_ is a command-line tool to capture network traffic.
- `Net-SNMP`_ command-line tools are great to see how your SNMP agent
  responds to requests.

Commercial Support
------------------

If you are still stuck, you might want to consider hiring a professional to
help you out.

`LeXtudio Inc.`_ does not only support PySNMP ecosystem by maintaining the
GitHub repositories but also offers commercial support such as consulting
services. You can easily open a support ticket via its homepage.

Related Resources
-----------------

- `Support Options`_
- :doc:`/quick-start`
- :doc:`/examples/index`
- :doc:`/docs/api-reference`
