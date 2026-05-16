import pytest

from pysnmp.proto.api import v2c
from pysnmp.smi.builder import MibBuilder
from pysnmp.smi.error import NoSuchInstanceError


def _make_mib_scalar_instance(syntax):
    mib_builder = MibBuilder()
    mib_builder.loadTexts = True
    _, MibScalarInstance = mib_builder.import_symbols(
        "SNMPv2-SMI", "MibScalar", "MibScalarInstance"
    )
    return MibScalarInstance((1, 3, 6, 1, 2, 1, 1, 1), (0,), syntax)


def test_schema_only_scalar_instance_read_get_raises_no_such_instance():
    scalar = _make_mib_scalar_instance(v2c.Integer())

    assert scalar.syntax.isValue is False

    with pytest.raises(NoSuchInstanceError):
        scalar.readGet((scalar.name, None))


def test_schema_only_scalar_instance_read_test_next_raises_no_such_instance():
    scalar = _make_mib_scalar_instance(v2c.Integer())

    assert scalar.syntax.isValue is False

    with pytest.raises(NoSuchInstanceError):
        scalar.readTestNext((scalar.name, None), oName=(1, 3, 6, 1, 2, 1, 1, 0))


def test_schema_only_scalar_instance_read_get_next_raises_no_such_instance():
    scalar = _make_mib_scalar_instance(v2c.Integer())

    assert scalar.syntax.isValue is False

    with pytest.raises(NoSuchInstanceError):
        scalar.readGetNext((scalar.name, None), oName=(1, 3, 6, 1, 2, 1, 1, 0))


def test_value_scalar_instance_read_get_returns_value():
    scalar = _make_mib_scalar_instance(v2c.Integer(5))

    assert scalar.syntax.isValue is True

    name, value = scalar.readGet((scalar.name, None))

    assert name == scalar.name
    assert value.isValue is True
    assert int(value) == 5
