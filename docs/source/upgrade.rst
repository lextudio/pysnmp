.. include:: /includes/_links.rst

Upgrade to 6.x/7.x Releases
===========================

.. toctree::
   :maxdepth: 2

This article provides information on how to upgrade to the latest 6.x/7.x
releases from old releases such as 4.x and 5.x.

.. note::

   If you have been using PySNMP packages with ``-lextudio`` postfix, now
   is the time to remove them and switch to the official PySNMP packages,
   which are maintained by LeXtudio Inc. as well.

   We already deprecated the ``-lextudio`` packages so users must migrate
   to the official packages as soon as possible.

Commercial Support for Migration
--------------------------------

.. important::

   **LeXtudio Inc. offers commercial support services** specifically to help organizations
   migrate from legacy 4.4.x releases to the latest versions. Professional assistance
   can significantly reduce migration time, ensure compatibility, and avoid common pitfalls.

   If you're managing critical infrastructure using older PySNMP releases, consider
   reaching out for expert guidance through the migration process.

   For more information on commercial support options, please visit `Support Options`_.

Upgrade to 5.x Releases
-----------------------

While working on 4.x releases, Ilya actually kept a master branch with some
experimental changes and planned to release as 5.0. However, this plan
wasn't finished and irrelevant to what you see today the 5.x releases from
other maintainers and their forks.

While various 5.0 releases were published by different maintainers, you
only see a single release by LeXtudio Inc., which is 5.1.0, on PyPI for
the official PySNMP project.

.. important::

   We only published 5.1.0 release, and we are not planning to publish any
   more 5.x releases. The 5.1.0 release was published to ensure smooth
   transition for users who are still using the 4.x releases.

   We consider the 5.1.0 release as a stepping stone to the 6.x releases,
   so please don't stay with them for long.

   You should next attempt to upgrade to 6.0.13 release and see if things
   work as expected.

   Note that you must use Python <3.12, as release 5.1.0 is not compatible
   with Python 3.12.

.. important::

   Each release has its own end-of-life date, so please check the table on
   `this lifecycle page`_ for more details.

Upgrade to 6.0 Releases
-----------------------

The 6.0 release is the first major release upgrade by LeXtudio Inc., after
the team took over the project and attempted twice internally to modernize
the code base. This release introduced the following changes:

* New changes required by Python 3.12 were applied, such as completely free
  of asyncore.
* Unit test coverage is further improved.
* New sync API based on asyncio is added to enable synchronous I/O
  operations and easy migration from 4.x/5.0 releases.
* The API surface was adjusted slightly to make it more aligned with other
  SNMP implementations.
* Upon better time synchronization in 5.0 release, more changes are
  included in 6.0 release to make the engine fully compliant with RFC3414.
* Documentation is significantly improved to cover the new features and
  changes.
* Continuous collaboration with downstream projects.

PySMI 1.3 and 1.4 releases introduced some changes that are not fully
compatible with PySMI 1.2. So we decided to keep PySNMP 6.0 with PySMI 1.2.

.. important::

   We only published 6.0.13 release, and we are not planning to publish any
   more 6.0 releases. The 6.0.13 release was published to ensure smooth
   transition for users who are still using the 4.x/5.x releases.

   We consider the 6.0.13 release as a stepping stone to the 6.1 releases,
   so please don't stay with them for long.

   You should first attempt to upgrade to 6.1.3 release and see if things
   work as expected.

.. important::

   Each release has its own end-of-life date, so please check the table on
   `this lifecycle page`_ for more details.

Upgrade to 6.1 Releases
-----------------------

We released PySNMP 6.1 release to support users who prefer PySMI 1.3 and
above. Ilya's changes for 4.4.13 release were merged as well.

.. important::

   We only published releases >=6.1.3, and we are not planning to publish
   many more 6.1 releases. Those releases were published to ensure smooth
   transition for users who are still using the 4.x/5.x/6.0 releases.

   We consider those releases as a stepping stone to the 6.2 releases,
   so please don't stay with them for long.

.. important::

   Each release has its own end-of-life date, so please check the table on
   `this lifecycle page`_ for more details.

Upgrade to 6.2 Releases
-----------------------

The new sync API was added in 6.0 releases to enable synchronous I/O
operations and easy migration from 4.x/5.x releases. The new API was based
on asyncio and was compatible with Python 3.8 and later.

We were hoping the new sync API would be stable enough to meet the quality
expectation, but it turned out to be the opposite. So we decided to remove
it from 6.2 release.

Alternatively, several options are there,

* You might copy the sync wrappers from 6.1 release and use
them in your code if you still need them.
* You might use other packages like [this one](https://pypi.prg/project/pysnmp-sync-adapter) which contains sync wrappers.

However, we are not maintaining those and will provide no support on them.

.. important::

   We published releases >=6.2.2, and we are not planning to publish any
   older 6.2 releases. The new 6.2 releases were published to ensure smooth
   transition for users who are still using the 4.x/5.x/6.0/6.1 releases.

.. important::

   Each release has its own end-of-life date, so please check the table on
   `this lifecycle page`_ for more details.

Upgrade to 7.0 Releases
-----------------------

The goals are

- Execute code base cleanup to meet PEP 8 requirements.
- Cherry-pick more patches from Ilya's old master branch for his planned
  5.0 release.

Breaking changes are

- Many fields and methods are renamed to meet PEP 8 requirements.
- Many types are moved to the newly introduced v3arch module.
- New types are introduced in v1arch module to simplify v1 and v2c operations.

.. important::

   Each release has its own end-of-life date, so please check the table on
   `this lifecycle page`_ for more details.

Upgrade to 7.1 Releases
-----------------------

The goals are

- Adapt to async DNS queries.
- Rework on GET NEXT and GET BULK related API surface.
- Apply more PEP 8 required changes.

Breaking changes are

- Transport type construction API is completely changed to support
  async DNS queries. For example, to create transport targets now users
  need to write ``await UdpTransportTarget.create()`` instead of
  ``UdpTransportTarget()``.
- ``next_cmd`` and ``bulk_cmd`` parameters and return types are revised.
- ``walk_cmd`` and ``bulk_walk_cmd`` are updated accordingly.
- Dropped Python 3.8 support.
- Due to method name changes to meet PEP 8, old names are marked as
  deprecated. While most of them are still working due to the compatibility
  layer, you should switch to the new names as soon as possible. **The
  compatibility layer will be removed in the next major release, 8.0.**

Related Resources
-----------------

- `Support Options`_
- :doc:`/troubleshooting`
- :doc:`/examples/index`
- :doc:`/docs/api-reference`
