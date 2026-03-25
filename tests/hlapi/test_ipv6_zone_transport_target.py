import asyncio
import socket
from unittest import mock

import pytest

from pysnmp.hlapi.v1arch.asyncio.transport import (
    Udp6TransportTarget as V1Udp6TransportTarget,
)
from pysnmp.hlapi.v3arch.asyncio.transport import (
    Udp6TransportTarget as V3Udp6TransportTarget,
)


def test_v1_udp6_transport_target_keeps_scope_id():
    loop = mock.AsyncMock()
    loop.getaddrinfo.return_value = [(None, None, None, None, ("fe80::1", 161, 0, 3))]

    with mock.patch("asyncio.get_event_loop", return_value=loop):
        target = asyncio.run(V1Udp6TransportTarget.create(("fe80::1%en0", 161)))

    assert target.transport_address == ("fe80::1", 161, 0, 3)


def test_v3_udp6_transport_target_keeps_scope_id():
    loop = mock.AsyncMock()
    loop.getaddrinfo.return_value = [(None, None, None, None, ("fe80::1", 161, 0, 3))]

    with mock.patch("asyncio.get_event_loop", return_value=loop):
        target = asyncio.run(V3Udp6TransportTarget.create(("fe80::1%en0", 161)))

    assert target.transport_address == ("fe80::1", 161, 0, 3)


def test_udp6_transport_target_wraps_gaierror():
    loop = mock.AsyncMock()
    loop.getaddrinfo.side_effect = socket.gaierror(-2, "Name or service not known")

    with mock.patch("asyncio.get_event_loop", return_value=loop):
        with pytest.raises(Exception, match="Bad IPv6/UDP transport address"):
            asyncio.run(V3Udp6TransportTarget.create(("bad-zone%missing", 161)))
