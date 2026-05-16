
Custom MibScalarInstance returns noSuchInstance
-----------------------------------------------

Q. I subclassed ``MibScalarInstance`` and override ``getValue()`` to
   compute the value on every read, but my Agent returns
   ``noSuchInstance`` (or ``genErr`` for SNMPv1) and ``getValue()`` is
   never called. Why?

A. The instance was constructed with a *schema-only* syntax object.

   In pyasn1, a type constructed without an argument (for example
   ``OctetString()`` or ``Integer32()``) is a *schema*: its
   ``isValue`` attribute is ``False``. ``MibScalarInstance.readTest``
   and ``readGet`` short-circuit and raise ``NoSuchInstanceError``
   whenever ``self.syntax.isValue`` is ``False`` — they never call
   ``getValue()``. This guards against truly uninitialized instances
   leaking ``noSuchInstance`` semantics through the agent.

   The fix is to pass an initial value to the instance constructor,
   even if your ``getValue()`` override is going to compute the real
   value at read time. Any value of the right type will do — an empty
   string, zero, etc. — its purpose is only to flip ``isValue`` to
   ``True``.

   .. code-block:: python

       class DynamicScalar(MibScalarInstance):
           def getValue(self, name, **context):
               return self.getSyntax().clone(compute_value_now())

       # WRONG: schema-only syntax, getValue() is never called
       DynamicScalar((1, 3, 6, 1, 4, 1, 60069, 9, 1), (0,), OctetString())

       # RIGHT: initialized syntax; getValue() is called on every read
       DynamicScalar((1, 3, 6, 1, 4, 1, 60069, 9, 1), (0,), OctetString(""))

   The same applies to ``Integer32(0)``, ``ObjectIdentifier((0, 0))``,
   and any other SMI type used as the ``syntax`` argument of a
   ``MibScalarInstance``.

   The schema/value distinction is intentional and is also what the
   companion ``MibScalar`` object relies on to advertise type
   information without claiming a value. Do not work around the check
   by stripping the ``isValue`` test — change the fixture instead.
