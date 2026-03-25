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
