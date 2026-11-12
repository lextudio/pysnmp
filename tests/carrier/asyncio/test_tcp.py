"""Tests for TCP asyncio stream transport."""

import asyncio
import struct
from unittest import mock

import pytest

from pysnmp.carrier.asyncio.stream.base import (
    StreamAsyncioProtocol,
    _TcpConnectionProtocol,
    _parse_ber_length,
)
from pysnmp.carrier.asyncio.stream.tcp import (
    SNMP_TCP_DOMAIN,
    TcpAsyncioTransport,
    TcpTransportAddress,
)


# ---------------------------------------------------------------------------
# _parse_ber_length
# ---------------------------------------------------------------------------


def test_parse_ber_length_short_form():
    data = bytes([0x30, 5, 0, 0, 0, 0, 0])
    total, header = _parse_ber_length(data)
    assert total == 7
    assert header == 2


def test_parse_ber_length_long_form_1_byte():
    data = bytes([0x30, 0x81, 10]) + bytes(10)
    total, header = _parse_ber_length(data)
    assert total == 13
    assert header == 3


def test_parse_ber_length_long_form_2_bytes():
    length = 300
    data = bytes([0x30, 0x82]) + struct.pack(">H", length) + bytes(length)
    total, header = _parse_ber_length(data)
    assert total == 4 + length
    assert header == 4


def test_parse_ber_length_returns_none_when_too_short():
    assert _parse_ber_length(b"") is None
    assert _parse_ber_length(bytes([0x30])) is None
    # long form but not enough length bytes
    assert _parse_ber_length(bytes([0x30, 0x82, 0x01])) is None


# ---------------------------------------------------------------------------
# TcpTransportAddress / SNMP_TCP_DOMAIN
# ---------------------------------------------------------------------------


def test_tcp_domain_oid():
    assert SNMP_TCP_DOMAIN == (1, 3, 6, 1, 6, 1, 3)


def test_tcp_transport_address():
    addr = TcpTransportAddress(("127.0.0.1", 161))
    assert addr[0] == "127.0.0.1"
    assert addr[1] == 161


# ---------------------------------------------------------------------------
# StreamAsyncioProtocol
# ---------------------------------------------------------------------------


def test_normalize_address_wraps_tuple():
    loop = asyncio.new_event_loop()
    try:
        t = TcpAsyncioTransport(loop=loop)
        addr = t.normalize_address(("10.0.0.1", 161))
        assert isinstance(addr, TcpTransportAddress)
    finally:
        loop.close()


def test_normalize_address_idempotent():
    loop = asyncio.new_event_loop()
    try:
        t = TcpAsyncioTransport(loop=loop)
        orig = TcpTransportAddress(("10.0.0.1", 161))
        addr = t.normalize_address(orig)
        assert addr is orig
    finally:
        loop.close()


# ---------------------------------------------------------------------------
# BER framing via _TcpConnectionProtocol
# ---------------------------------------------------------------------------


def _make_ber_message(payload: bytes) -> bytes:
    """Wrap payload in a minimal BER SEQUENCE envelope."""
    length = len(payload)
    if length < 0x80:
        return bytes([0x30, length]) + payload
    elif length <= 0xFF:
        return bytes([0x30, 0x81, length]) + payload
    else:
        return bytes([0x30, 0x82]) + struct.pack(">H", length) + payload


def _make_transport_and_proto():
    loop = asyncio.new_event_loop()
    received = []
    transport = TcpAsyncioTransport(loop=loop)
    transport._callback_function = lambda t, addr, msg: received.append(msg)
    peer = TcpTransportAddress(("127.0.0.1", 12345))
    proto = _TcpConnectionProtocol(transport, peer)
    # Simulate connection_made without a real socket
    mock_transport = mock.Mock()
    mock_transport.get_extra_info.return_value = ("127.0.0.1", 12345)
    proto.connection_made(mock_transport)
    return loop, transport, proto, received


def test_single_complete_message_delivered():
    loop, transport, proto, received = _make_transport_and_proto()
    try:
        msg = _make_ber_message(b"\x02\x01\x00")  # simple payload
        proto.data_received(msg)
        loop.run_until_complete(asyncio.sleep(0))  # let call_soon fire
        assert len(received) == 1
        assert received[0] == msg
    finally:
        loop.close()


def test_fragmented_message_buffered_then_delivered():
    loop, transport, proto, received = _make_transport_and_proto()
    try:
        payload = b"\x00" * 10
        msg = _make_ber_message(payload)
        half = len(msg) // 2
        proto.data_received(msg[:half])
        loop.run_until_complete(asyncio.sleep(0))
        assert received == [], "incomplete message should not be delivered"
        proto.data_received(msg[half:])
        loop.run_until_complete(asyncio.sleep(0))
        assert len(received) == 1
        assert received[0] == msg
    finally:
        loop.close()


def test_two_messages_in_one_chunk_both_delivered():
    loop, transport, proto, received = _make_transport_and_proto()
    try:
        msg1 = _make_ber_message(b"\x01\x02\x03")
        msg2 = _make_ber_message(b"\x04\x05\x06")
        proto.data_received(msg1 + msg2)
        loop.run_until_complete(asyncio.sleep(0))
        assert len(received) == 2
        assert received[0] == msg1
        assert received[1] == msg2
    finally:
        loop.close()


# ---------------------------------------------------------------------------
# Deprecated attribute access
# ---------------------------------------------------------------------------


def test_deprecated_attribute_raises_warning():
    loop = asyncio.new_event_loop()
    try:
        t = TcpAsyncioTransport(loop=loop)
        with pytest.warns(DeprecationWarning, match="openClientMode"):
            method = t.openClientMode
        assert method == t.open_client_mode
    finally:
        loop.close()


def test_unknown_attribute_raises_attribute_error():
    loop = asyncio.new_event_loop()
    try:
        t = TcpAsyncioTransport(loop=loop)
        with pytest.raises(AttributeError):
            _ = t.no_such_attribute
    finally:
        loop.close()


# ---------------------------------------------------------------------------
# open_server_mode / close_transport (integration, real loop)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_open_server_mode_and_close():
    loop = asyncio.get_event_loop()
    t = TcpAsyncioTransport(loop=loop)
    t._callback_function = mock.Mock()
    t.open_server_mode(iface=("127.0.0.1", 0))
    # Allow the server future to complete
    await asyncio.sleep(0.05)
    t.close_transport()


@pytest.mark.asyncio
async def test_connect_send_receive():
    """End-to-end: client sends one message; server receives it."""
    loop = asyncio.get_event_loop()

    server_received = []

    def on_recv(transport, addr, msg):
        server_received.append(msg)

    # Server
    server = TcpAsyncioTransport(loop=loop)
    server._callback_function = on_recv
    server.open_server_mode(iface=("127.0.0.1", 0))
    await asyncio.sleep(0.05)

    # Determine the port the server bound to
    server_future = server._lport
    srv_obj = await server_future
    server._server = srv_obj
    port = srv_obj.sockets[0].getsockname()[1]

    # Client
    client = TcpAsyncioTransport(loop=loop)
    client._callback_function = mock.Mock()

    payload = b"\x02\x01\x00" * 3
    msg = _make_ber_message(payload)
    client.send_message(msg, ("127.0.0.1", port))
    await asyncio.sleep(0.2)

    assert len(server_received) == 1
    assert server_received[0] == msg

    client.close_transport()
    server.close_transport()
