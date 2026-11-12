import asyncio
import importlib
import socket
import sys
from unittest import mock

import pytest

from pysnmp.carrier.asyncio.dgram import udp6


def test_udp6_normalize_address_strips_zone_id():
    transport = udp6.Udp6Transport(loop=asyncio.new_event_loop())

    normalized = transport.normalize_address(("fe80::1%eth0", 161))

    assert normalized[0] == "fe80::1"
    assert normalized[1] == 161
    assert normalized[2] == 0
    assert normalized[3] == 0


def test_udp6_transport_sets_ipv6_transparent_constant(monkeypatch):
    monkeypatch.delattr(socket, "IPV6_TRANSPARENT", raising=False)

    module_name = "pysnmp.carrier.sockfix"
    if module_name in sys.modules:
        del sys.modules[module_name]

    sockfix = importlib.import_module(module_name)

    assert hasattr(socket, "IPV6_TRANSPARENT")
    assert socket.IPV6_TRANSPARENT == 75
    assert sockfix.SYMBOLS["IPV6_TRANSPARENT"] == 75


@pytest.mark.asyncio
async def test_udp6_transport_send_receive_loopback():
    if not socket.has_ipv6:
        pytest.skip("IPv6 is not available on this platform")

    loop = asyncio.get_event_loop()
    received = []

    def on_receive(transport, addr, msg):
        received.append(msg)

    server = udp6.Udp6Transport(loop=loop)
    server._callback_function = on_receive
    server.open_server_mode(iface=("::1", 0))
    await asyncio.sleep(0.05)

    server_future = server._lport
    server_transport, _ = await server_future
    port = server_transport.get_extra_info("sockname")[1]

    client = udp6.Udp6Transport(loop=loop)
    client._callback_function = mock.Mock()
    client.open_client_mode(iface=("::1", 0))
    await asyncio.sleep(0.05)

    payload = b"snmp-ipv6-test"
    client.send_message(payload, ("::1", port))

    await asyncio.sleep(0.05)

    assert received == [payload]

    client.close_transport()
    server.close_transport()
