import asyncio
from unittest import mock

from pysnmp.carrier.asyncio.dispatch import AsyncioDispatcher


def test_asyncio_dispatcher_uses_provided_loop_without_touching_global_loop():
    provided_loop = mock.Mock()

    with mock.patch(
        "pysnmp.carrier.asyncio.dispatch.asyncio.get_event_loop",
        side_effect=AssertionError("get_event_loop should not be called"),
    ):
        dispatcher = AsyncioDispatcher(loop=provided_loop)

    assert dispatcher.loop is provided_loop


def test_asyncio_dispatcher_uses_global_loop_when_not_provided():
    provided_loop = mock.Mock()

    with mock.patch(
        "pysnmp.carrier.asyncio.dispatch.asyncio.get_event_loop",
        return_value=provided_loop,
    ) as get_event_loop:
        dispatcher = AsyncioDispatcher()

    assert dispatcher.loop is provided_loop
    get_event_loop.assert_called_once_with()


def test_asyncio_dispatcher_preserves_explicit_none_loop():
    with mock.patch(
        "pysnmp.carrier.asyncio.dispatch.asyncio.get_event_loop",
        side_effect=AssertionError("get_event_loop should not be called"),
    ):
        dispatcher = AsyncioDispatcher(loop=None)

    assert dispatcher.loop is None


def test_close_dispatcher_stops_running_event_loop():
    """Test that close_dispatcher stops the loop when run_dispatcher started it."""
    loop = asyncio.new_event_loop()
    dispatcher = AsyncioDispatcher(loop=loop)

    # Simulate run_dispatcher having started the loop
    dispatcher._AsyncioDispatcher__run_dispatcher_started_loop = True  # type: ignore[attr-defined]

    # Mock current_task to return None (we're not in the event loop)
    with mock.patch("asyncio.current_task", return_value=None):
        dispatcher.close_dispatcher()

    assert not loop.is_running()
    loop.close()


def test_close_dispatcher_multiple_times_is_safe():
    loop = asyncio.new_event_loop()
    dispatcher = AsyncioDispatcher(loop=loop)

    dispatcher.close_dispatcher()
    dispatcher.close_dispatcher()
    dispatcher.close_dispatcher()

    loop.close()


def test_close_dispatcher_before_run_dispatcher_is_safe():
    loop = asyncio.new_event_loop()
    dispatcher = AsyncioDispatcher(loop=loop)

    dispatcher.close_dispatcher()
    assert not loop.is_running()

    loop.close()


def test_run_dispatcher_exits_when_closed():
    loop = asyncio.new_event_loop()
    dispatcher = AsyncioDispatcher(loop=loop)

    async def close_after_delay():
        await asyncio.sleep(0.1)
        dispatcher.close_dispatcher()

    async def main():
        await close_after_delay()

    loop.run_until_complete(main())

    assert not loop.is_running()
    loop.close()


def test_close_dispatcher_does_not_leave_pending_timer_task():
    """#256: the timer task must be finished, not left in 'cancelling'."""
    loop = asyncio.new_event_loop()
    try:
        dispatcher = AsyncioDispatcher(loop=loop)
        dispatcher.register_transport((1, 3, 6, 1), mock.MagicMock())
        loop.run_until_complete(asyncio.sleep(0))
        task = dispatcher.loopingcall
        assert task is not None

        dispatcher.close_dispatcher()

        assert task.done()
        assert not [t for t in asyncio.all_tasks(loop) if not t.done()]
    finally:
        loop.close()


def test_close_transport_does_not_leave_pending_listener_task():
    """#256: closing a transport before the loop ran must not leave a pending task."""
    from pysnmp.carrier.asyncio.dgram.udp import UdpAsyncioTransport

    loop = asyncio.new_event_loop()
    try:
        transport = UdpAsyncioTransport(loop=loop).open_server_mode(("127.0.0.1", 0))
        task = transport._lport
        assert not task.done()

        transport.close_transport()

        assert task.done()
    finally:
        loop.close()
