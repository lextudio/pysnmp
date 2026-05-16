#
# This file is part of pysnmp software.
#
# Copyright (C) 2024, LeXtudio Inc. <support@lextudio.com>
# License: https://www.pysnmp.com/pysnmp/license.html
#
"""
StreamAsyncioProtocol is a base class for asyncio stream (TCP) transport.

TCP is connection-oriented, so each peer connection is tracked separately.
BER message framing is used to extract complete SNMP messages from the stream.
"""

import asyncio
import sys
import traceback
import warnings

from pysnmp import debug
from pysnmp.carrier import error
from pysnmp.carrier.asyncio.base import AbstractAsyncioTransport
from pysnmp.carrier.base import AbstractTransportAddress


def _parse_ber_length(data: bytes) -> "tuple[int, int] | None":
    """Return (total_message_length, header_bytes) from a BER SEQUENCE header.

    Returns None if there are not enough bytes yet to determine the length.
    """
    if len(data) < 2:
        return None
    # data[0] should be 0x30 (SEQUENCE tag) for a valid SNMP message
    length_byte = data[1]
    if length_byte < 0x80:
        # Short form: length is in this byte
        return 2 + length_byte, 2
    num_length_bytes = length_byte & 0x7F
    if len(data) < 2 + num_length_bytes:
        return None
    length = int.from_bytes(data[2 : 2 + num_length_bytes], "big")
    header = 2 + num_length_bytes
    return header + length, header


class _TcpConnectionProtocol(asyncio.Protocol):
    """Per-connection protocol handling for a single TCP connection."""

    def __init__(self, owner: "StreamAsyncioProtocol", peer_address):
        self._owner = owner
        self._peer_address = peer_address
        self._transport: "asyncio.Transport | None" = None
        self._buffer = b""

    def connection_made(self, transport: asyncio.Transport):
        self._transport = transport
        peer = transport.get_extra_info("peername")
        if peer:
            self._peer_address = self._owner.ADDRESS_TYPE(peer[:2])
        self._owner._register_connection(self._peer_address, self)
        debug.logger & debug.FLAG_IO and debug.logger(
            f"TCP connection_made: peer {self._peer_address!r}"
        )

    def data_received(self, data: bytes):
        self._buffer += data
        while True:
            if not self._buffer:
                break
            result = _parse_ber_length(self._buffer)
            if result is None:
                break
            msg_len, _ = result
            if len(self._buffer) < msg_len:
                break
            message = self._buffer[:msg_len]
            self._buffer = self._buffer[msg_len:]
            debug.logger & debug.FLAG_IO and debug.logger(
                "TCP data_received: peer %r message %s"
                % (self._peer_address, debug.hexdump(message))
            )
            if self._owner._callback_function is not None:
                self._owner.loop.call_soon(
                    self._owner._callback_function,
                    self._owner,
                    self._peer_address,
                    message,
                )

    def connection_lost(self, exc):
        debug.logger & debug.FLAG_IO and debug.logger(
            f"TCP connection_lost: peer {self._peer_address!r}"
        )
        self._owner._unregister_connection(self._peer_address)

    def send(self, data: bytes):
        if self._transport is not None:
            self._transport.write(data)


class StreamAsyncioProtocol(AbstractAsyncioTransport):
    """Base asyncio TCP stream transport, to be used with AsyncioDispatcher."""

    SOCK_FAMILY: int = 0
    ADDRESS_TYPE: type

    def __init__(self, sock=None, sockMap=None, loop=None):
        self._connections: "dict[tuple, _TcpConnectionProtocol]" = {}
        self._server: "asyncio.AbstractServer | None" = None
        self._client_proto: "_TcpConnectionProtocol | None" = None
        self._pending_writes: "list[tuple[bytes, tuple]]" = []
        self._lport = None
        if loop is None:
            loop = asyncio.get_event_loop()
        self.loop = loop

    def _register_connection(self, addr, proto: _TcpConnectionProtocol):
        self._connections[tuple(addr)] = proto
        # Flush any pending writes for this address
        remaining = []
        for msg, dest in self._pending_writes:
            if tuple(dest) == tuple(addr):
                proto.send(msg)
            else:
                remaining.append((msg, dest))
        self._pending_writes = remaining

    def _unregister_connection(self, addr):
        self._connections.pop(tuple(addr), None)

    def open_client_mode(self, iface=None, allow_broadcast=False):
        """Not used for TCP; connections are initiated per send_message."""
        return self

    def open_server_mode(self, iface=None, sock=None):
        """Start a TCP server listening on iface."""
        if iface is None and sock is None:
            raise error.CarrierError("either iface or sock is required")
        if self.loop.is_closed():
            raise error.CarrierError("Event loop is closed")
        try:
            coro = self.loop.create_server(
                lambda: _TcpConnectionProtocol(self, None),
                host=iface[0] if iface else None,
                port=iface[1] if iface else None,
                sock=sock,
                family=self.SOCK_FAMILY,
            )
            self._lport = asyncio.ensure_future(coro)
        except Exception:
            raise error.CarrierError(
                ";".join(traceback.format_exception(*sys.exc_info()))
            )
        return self

    def close_transport(self):
        """Close all connections and the server."""
        if self._lport is not None:
            self._lport.cancel()
        if self._server is not None:
            self._server.close()
        for proto in list(self._connections.values()):
            if proto._transport:
                proto._transport.close()
        self._connections.clear()
        AbstractAsyncioTransport.close_transport(self)

    def send_message(self, outgoingMessage, transportAddress):
        """Send message to transportAddress, establishing a connection if needed."""
        addr = self.normalize_address(transportAddress)
        key = tuple(addr)
        debug.logger & debug.FLAG_IO and debug.logger(
            "TCP sendMessage: transportAddress %r outgoingMessage %s"
            % (addr, debug.hexdump(outgoingMessage))
        )
        if key in self._connections:
            self._connections[key].send(outgoingMessage)
        else:
            # Queue message and open a new connection
            self._pending_writes.append((outgoingMessage, key))
            try:
                coro = self.loop.create_connection(
                    lambda: _TcpConnectionProtocol(self, addr),
                    host=addr[0],
                    port=addr[1],
                    family=self.SOCK_FAMILY,
                )
                asyncio.ensure_future(coro)
            except Exception:
                raise error.CarrierError(
                    ";".join(traceback.format_exception(*sys.exc_info()))
                )

    def normalize_address(self, transportAddress):
        if not isinstance(transportAddress, self.ADDRESS_TYPE):
            transportAddress = self.ADDRESS_TYPE(transportAddress)
        return transportAddress

    deprecated_attributes = {
        "openClientMode": "open_client_mode",
        "openServerMode": "open_server_mode",
        "closeTransport": "close_transport",
        "sendMessage": "send_message",
        "normalizeAddr": "normalize_address",
    }

    def __getattr__(self, attr: str):
        if new_attr := self.deprecated_attributes.get(attr):
            warnings.warn(
                f"{attr} is deprecated. Please use {new_attr} instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            return getattr(self, new_attr)
        raise AttributeError(
            f"class '{self.__class__.__name__}' has no attribute '{attr}'"
        )
