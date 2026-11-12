"""Regression tests for the snmpEngineTime 2038 overflow (issue #205).

RFC 3411 §5.3.1 defines ``snmpEngineTime`` as ``INTEGER (0..2147483647)``
holding the seconds elapsed since ``snmpEngineBoots`` last changed. The engine
initialised it with the raw Unix time, which stops fitting that range on
2038-01-19. From then on ``SnmpEngine()`` itself could not be constructed::

    MibLoadError -> ValueConstraintError: 2179019648

There is a second, quieter half to this. The live value is produced by
subtracting the stored base from the current time, and that subtraction goes
through pyasn1's ``__rsub__``, which calls ``clone()`` again. On an
out-of-range result that raises, and the surrounding ``except Exception: pass``
swallowed it -- so the engine time silently degraded to the raw base instead of
the elapsed seconds.

These tests pin both halves.
"""

import time

import pytest

# RFC 3411 §5.3.1: snmpEngineTime ::= INTEGER (0..2147483647)
MAX_ENGINE_TIME = 2147483647

UNIX_2038_BOUNDARY = MAX_ENGINE_TIME  # 2038-01-19T03:14:07Z
CLOCK_2040 = 2179019648
CLOCK_FAR_FUTURE = 10**12


@pytest.fixture
def fake_clock(monkeypatch):
    """Set the wall clock. Each engine is built fresh, so it re-reads this."""

    def _set(value):
        monkeypatch.setattr(time, "time", lambda: value)

    return _set


def _engine_time_syntax():
    """A fresh engine re-executes the MIB instance module, re-reading the clock."""
    from pysnmp.entity import engine

    snmp_engine = engine.SnmpEngine()
    (instance,) = snmp_engine.get_mib_builder().import_symbols(
        "__SNMP-FRAMEWORK-MIB", "snmpEngineTime"
    )
    return instance.syntax


@pytest.mark.parametrize(
    "clock",
    [
        pytest.param(UNIX_2038_BOUNDARY - 1, id="just-below-2038"),
        pytest.param(UNIX_2038_BOUNDARY, id="at-2038-boundary"),
        pytest.param(UNIX_2038_BOUNDARY + 1, id="one-second-past-2038"),
        pytest.param(CLOCK_2040, id="2040"),
        pytest.param(3800000000, id="2090"),
        pytest.param(CLOCK_FAR_FUTURE, id="far-future"),
    ],
)
def test_engine_constructs_past_2038(fake_clock, clock):
    """SnmpEngine() must not raise once the wall clock passes 2038-01-19."""
    fake_clock(clock)

    syntax = _engine_time_syntax()  # must not raise

    assert int(syntax.clone()) <= MAX_ENGINE_TIME


def test_served_value_is_elapsed_not_absolute(fake_clock):
    """The served value must count up from engine start, not echo Unix time."""
    fake_clock(CLOCK_2040)

    syntax = _engine_time_syntax()
    assert int(syntax.clone()) == 0, "a freshly built engine has elapsed 0s"

    fake_clock(CLOCK_2040 + 3600)
    assert int(syntax.clone()) == 3600

    fake_clock(CLOCK_2040 + 86400)
    assert int(syntax.clone()) == 86400


def test_served_value_tracks_a_moving_clock(fake_clock):
    """Sanity check that the value follows the clock rather than sticking."""
    fake_clock(CLOCK_2040)

    syntax = _engine_time_syntax()
    seen = []
    for offset in (0, 1, 60, 3600, 86400):
        fake_clock(CLOCK_2040 + offset)
        seen.append(int(syntax.clone()))

    assert seen == [0, 1, 60, 3600, 86400]
    assert seen == sorted(seen), "engine time must be monotonic"


def test_served_value_wraps_instead_of_overflowing(fake_clock):
    """Past a 68-year span it must wrap, not raise or go out of range."""
    fake_clock(CLOCK_2040)

    syntax = _engine_time_syntax()
    fake_clock(CLOCK_2040 + MAX_ENGINE_TIME + 5000)

    served = int(syntax.clone())
    assert 0 <= served <= MAX_ENGINE_TIME
    assert served == 5000, "should wrap to the remainder"


def test_engine_time_keeps_its_integer32_encoding(fake_clock):
    """Guard against 'fixing' the overflow by widening the type.

    PR #35 proposed Integer32 -> Unsigned32. In the SMI that carries the
    Gauge32 application tag, so it would change the BER encoding of
    snmpEngineTime and break conformance with RFC 3411's
    ``INTEGER (0..2147483647)``.
    """
    from pysnmp.proto.rfc1902 import Integer32, Unsigned32

    fake_clock(CLOCK_2040)

    syntax = _engine_time_syntax()

    assert syntax.tagSet == Integer32().tagSet, "must stay a plain INTEGER"
    assert syntax.tagSet != Unsigned32().tagSet, "must not become Gauge32"
