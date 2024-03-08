.. include:: /includes/_links.rst

Upgrade to 6.0 Release
======================

.. toctree::
   :maxdepth: 2

This article provides information on how to upgrade to the latest 6.0
release from earlier releases such as 4.x and 5.x.

Issues in 4.x Releases
----------------------

The old releases were finished before 2020 by Ilya Etingof and wasn't well
maintained since 2019. While Ilya kept the project alive, the project was
not living up to its potential nor following the best practices of the
modern software development,

1. Many legacy code existed to keep compatibility with very old Python
   versions like 2.x. That added unnecessary complexity to the project and
   made it hard to maintain and develop new features.
1. The core library was not well covered by unit test cases. So when
   certain features were added or patched, and listed in release notes, not
   enough information is available on why the changes were needed. And even
   if we wanted to clean up or refactor the code, we couldn't do it easily
   without breaking the existing functionality.

Issues in 5.0 Release
---------------------

It took the Splunk team and LeXtudio Inc. several months to get familiar
with the code base and applied various ways to advance the project. In
short,

* The build system was migrated to poetry, which is a modern Python
  packaging tool that simplifies the process of packaging and distributing
  Python packages. Testing the bits on Python 3.8-3.12 couldn't be easier.
* Legacy code for Python 2.x was removed, while changes required by Python
  3.11/3.12 was applied.
* Patches created by the community between 2019 and 2022 were gradually
  merged into the code base.
* Testing started to become a top priority, either through integration
  tests or unit tests.
* The API surface was kept compatible with the 4.x releases in most cases.
* Documentation was updated to reflect the changes.

Upgrade to 6.0
--------------

The 6.0 release is the first major release upgrade by LeXtudio Inc., after
the team took over the project and attempted twice internally to modernize
the code base. So far, this release introduces the following changes:

* Unit test coverage is significantly improved.
* Legacy API based on asyncore has been completely removed.
* New sync API based on asyncio is added to enable synchronous I/O
  operations and easy migration from 4.x/5.0 releases.
* Documentation is significantly improved to cover the new features and
  changes.

Important Changes
-----------------

The following changes are important to note when upgrading to 6.0:

Async API based on asyncore
+++++++++++++++++++++++++++

All such APIs are removed, so you can no longer import types from the
relevant modules. This includes sync API based on asyncore.

Sync API based on asyncio
+++++++++++++++++++++++++

The new sync API is added to enable synchronous I/O operations and easy
migration from 4.x/5.0 releases. The new API is based on asyncio and is
compatible with Python 3.8 and later.

However, the new sync API is not a drop-in replacement for the old sync
API. For example,

* The old sync API returns a ``Generator`` object where you can iterate
  through the ``tuple`` of response data, while the new sync API simply
  returns the ``tuple`` so you know you are doing a single SNMP request.

  So if the following code is used for a single request operation, where
  ``next()`` iterates over the ``Generator`` object,

  .. code:: python

     errorIndication, errorStatus, errorIndex, varBinds = next(getCmd(
            snmpEngine,
            CommunityData("public", mpModel=0),
            UdpTransportTarget(("demo.pysnmp.com", 161)),
            ContextData(),
            ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)),
        )
     )

  now with the new sync API, you can simply do,

  .. code:: python

        errorIndication, errorStatus, errorIndex, varBinds = getCmd(
            snmpEngine,
            CommunityData("public", mpModel=0),
            UdpTransportTarget(("demo.pysnmp.com", 161)),
            ContextData(),
            ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)),
        )

* To keep supporting composite operations such as WALK, new methods like
  ``walkCmd`` and ``bulkWalkCmd`` are added. The method names are more
  aligned with other SNMP implementations, and the method signatures are
  intentionally different from single request methods like ``getCmd``.

  ``walkCmd`` works more similar to ``nextCmd`` in 4.x/5.0 releases, while
  ``bulkWalkCmd`` works more similar to ``bulkCmd``.

RFC3414 Compliance
++++++++++++++++++

The engine request/response processing wasn't fully compliant with RFC3414,
especially when it came to error handling.

Initial changes were introduced to better support time synchronization in
5.0 release, but more changes are included in 6.0 release to make the
engine fully compliant with RFC3414.

References
----------

- `Support Options`_
- :doc:`/troubleshooting`
- :doc:`/examples/index`
- :doc:`/docs/api-reference`
