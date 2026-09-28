"""Regression tests for the Python 3.14 event loop change (issue #240).

Up to 3.13, ``asyncio.get_event_loop()`` created an event loop implicitly when
the calling thread had none. Python 3.14 removed that behaviour and raises
``RuntimeError: There is no current event loop in thread 'MainThread'``
instead, so constructing a dispatcher or a transport outside a running loop --
for example inside a ``multiprocessing`` child process -- started failing.

The affected call sites were the three in the asyncio carrier layer. The hlapi
sites sit inside coroutines, where a loop is already running, so they were not
affected.

The tests clear the current event loop explicitly so the fallback is exercised
on every Python version, not only on 3.14+.
"""

import asyncio

import pytest

from pysnmp.carrier.asyncio.dgram import udp
from pysnmp.carrier.asyncio.dispatch import AsyncioDispatcher
from pysnmp.carrier.asyncio.stream import tcp


@pytest.fixture
def no_current_event_loop():
    """Run the test with no event loop set on this thread, then restore it."""
    try:
        previous = asyncio.get_event_loop_policy().get_event_loop()
    except RuntimeError:
        previous = None

    asyncio.set_event_loop(None)
    try:
        yield
    finally:
        asyncio.set_event_loop(previous)


def test_dispatcher_gets_a_loop_without_a_current_one(no_current_event_loop):
    dispatcher = AsyncioDispatcher()
    try:
        assert isinstance(dispatcher.loop, asyncio.AbstractEventLoop)
    finally:
        dispatcher.close_dispatcher()


def test_udp_transport_gets_a_loop_without_a_current_one(no_current_event_loop):
    transport = udp.UdpAsyncioTransport()
    try:
        assert isinstance(transport.loop, asyncio.AbstractEventLoop)
    finally:
        transport.close_transport()


def test_tcp_transport_gets_a_loop_without_a_current_one(no_current_event_loop):
    transport = tcp.TcpAsyncioTransport()
    try:
        assert isinstance(transport.loop, asyncio.AbstractEventLoop)
    finally:
        transport.close_transport()


def test_explicit_loop_is_still_honoured(no_current_event_loop):
    """An explicitly supplied loop must win over the fallback."""
    loop = asyncio.new_event_loop()
    try:
        assert AsyncioDispatcher(loop=loop).loop is loop
        assert udp.UdpAsyncioTransport(loop=loop).loop is loop
        assert tcp.TcpAsyncioTransport(loop=loop).loop is loop
    finally:
        loop.close()
