"""Regression tests for the USM timeline cache expiry (issue #245).

The cached non-authoritative engine timeline is refreshed on every
authenticated message. It used to register a *new* expiry bucket for the
engine each time without cancelling the previous registration, so a stale
bucket would later expire a freshly refreshed entry. In steady polling the
timeline was therefore destroyed roughly 300 seconds after it was learned and
never recovered, making every request pay an extra
``usmStatsNotInTimeWindows`` round trip.
"""

from pysnmp.proto.secmod.rfc3414 import service

ENGINE_ID = "0x800097b60368ebc500d688"


class _NoDispatcherEngine:
    """Minimal stand-in: no transport dispatcher means 1s timer resolution."""

    transport_dispatcher = None


def _make_service():
    svc = service.SnmpUSMSecurityModel()
    priv = "_SnmpUSMSecurityModel__"
    return (
        svc,
        priv,
        lambda: getattr(svc, priv + "timeline"),
        lambda: getattr(svc, priv + "timelineExpQueue"),
        lambda: getattr(svc, priv + "timelineExpiry"),
        lambda: getattr(svc, priv + "expirationTimer"),
        getattr(svc, priv + "expire_timeline_info"),
        getattr(svc, priv + "schedule_timeline_expiry"),
    )


def test_timeline_survives_steady_polling():
    """Refreshing the timeline must not let a stale bucket expire it."""
    _, _, timeline, exp_queue, expiry_map, timer, tick, schedule = _make_service()

    engine = _NoDispatcherEngine()
    first_wipe = None

    for i in range(1000):
        # mirrors the "synchronize time with authed peer" store in
        # processIncomingMsg
        timeline()[ENGINE_ID] = (2, i, i, 0)
        schedule(ENGINE_ID, engine)
        tick()
        if ENGINE_ID not in timeline() and first_wipe is None:
            first_wipe = timer()

    assert first_wipe is None, (
        "timeline was expired by a stale registration at tick %s" % first_wipe
    )
    assert ENGINE_ID in timeline()
    # the expiry queue must not grow by one bucket per received message
    assert len(exp_queue()) == 1
    assert len(expiry_map()) == 1


def test_timeline_still_expires_after_idle_period():
    """The 300s safety valve must still evict an idle timeline entry."""
    _, _, timeline, exp_queue, expiry_map, _, tick, schedule = _make_service()

    engine = _NoDispatcherEngine()
    timeline()[ENGINE_ID] = (2, 1, 1, 0)
    schedule(ENGINE_ID, engine)

    # a bucket is processed on the tick that starts at its expireAt, so the
    # entry registered at timer 0 for expireAt 300 goes on tick 301
    for _ in range(300):
        tick()
    assert ENGINE_ID in timeline(), "expired before the 300s deadline"

    tick()
    assert ENGINE_ID not in timeline(), "did not expire at the 300s deadline"
    assert not exp_queue(), "expiry queue not drained"
    assert not expiry_map(), "pending expiry bookkeeping not cleared"


def test_timeline_recovers_after_expiry():
    """A timeline re-learned from a report must stay warm afterwards."""
    _, _, timeline, _, _, _, tick, schedule = _make_service()

    engine = _NoDispatcherEngine()
    timeline()[ENGINE_ID] = (2, 1, 1, 0)
    schedule(ENGINE_ID, engine)

    for _ in range(301):
        tick()
    assert ENGINE_ID not in timeline()

    # re-learned from the usmStatsNotInTimeWindows report
    timeline()[ENGINE_ID] = (2, 5000, 5000, 0)
    schedule(ENGINE_ID, engine)

    for _ in range(200):
        tick()
    assert ENGINE_ID in timeline(), "re-learned timeline was expired again"


def test_multiple_engines_expire_independently():
    """Per-engine bookkeeping must not let one engine evict another."""
    _, _, timeline, _, _, _, tick, schedule = _make_service()

    engine = _NoDispatcherEngine()
    other = "0x80009fb8030102e5c4a10a"

    timeline()[ENGINE_ID] = (2, 1, 1, 0)
    schedule(ENGINE_ID, engine)
    timeline()[other] = (5, 2, 2, 0)
    schedule(other, engine)

    # keep refreshing only ENGINE_ID; `other` should still age out
    for _ in range(301):
        timeline()[ENGINE_ID] = (2, 1, 1, 0)
        schedule(ENGINE_ID, engine)
        tick()

    assert ENGINE_ID in timeline()
    assert other not in timeline()
