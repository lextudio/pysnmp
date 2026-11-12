import pytest

from pysnmp.proto.api import v2c
from pysnmp.smi import exval
from pysnmp.smi.builder import MibBuilder
from pysnmp.smi.error import NoSuchInstanceError
from pysnmp.smi.instrum import MibInstrumController


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


def test_read_test_next_uses_candidate_oid():
    mib_builder = MibBuilder()
    MibScalar, MibScalarInstance, MibIdentifier, Integer32 = mib_builder.import_symbols(
        "SNMPv2-SMI", "MibScalar", "MibScalarInstance", "MibIdentifier", "Integer32"
    )
    base = (1, 3, 6, 1, 4, 1, 99999, 1)
    tested_oids = []

    class RecordingInstance(MibScalarInstance):
        def readTestNext(self, varBind, **context):  # noqa: N802
            tested_oids.append(varBind[0])
            return super().readTestNext(varBind, **context)

    mib_builder.export_symbols(
        "__TEST-MIB",
        root=MibIdentifier(base),
        first=MibScalar(base + (1,), Integer32()),
        first_instance=RecordingInstance(base + (1,), (0,), Integer32(1)),
        second=MibScalar(base + (2,), Integer32()),
        second_instance=RecordingInstance(base + (2,), (0,), Integer32(2)),
    )
    controller = MibInstrumController(mib_builder)

    result = controller.read_next_variables((base + (1, 0), None))

    assert result[0][0] == base + (2, 0)
    assert int(result[0][1]) == 2
    assert tested_oids == [base + (1, 0), base + (2, 0)]

    end_of_mib = controller.read_next_variables((base + (2, 0), None))

    assert end_of_mib == [(base + (2, 0), exval.endOfMib)]
