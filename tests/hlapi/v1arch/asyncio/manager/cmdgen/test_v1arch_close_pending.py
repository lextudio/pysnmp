"""Regression tests for #258: close() with a request still pending.

Like the v3arch dispatcher, close() drops pending requests without calling
their callbacks, so a cancelled caller sees its cancellation, not a TypeError.
"""

import asyncio
import socket

import pytest
from pysnmp.hlapi.v1arch.asyncio import *
from pysnmp.proto.rfc1902 import OctetString
from pysnmp.smi.rfc1902 import NotificationType, ObjectIdentity, ObjectType


@pytest.fixture
def silent_port():
    silent = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    silent.bind(("127.0.0.1", 0))
    yield silent.getsockname()[1]
    silent.close()


@pytest.mark.asyncio
async def test_close_with_pending_get_does_not_replace_cancellation(silent_port):
    async def snmp_get():
        dispatcher = SnmpDispatcher()
        try:
            transport = await UdpTransportTarget.create(
                ("127.0.0.1", silent_port), timeout=2.0, retries=0
            )
            return await get_cmd(
                dispatcher,
                CommunityData("public", mpModel=1),
                transport,
                ObjectType(ObjectIdentity("1.3.6.1.2.1.1.3.0")),
            )
        finally:
            dispatcher.close()

    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(snmp_get(), 0.5)


@pytest.mark.asyncio
@pytest.mark.parametrize("command", ["get", "next", "set", "bulk", "notify"])
async def test_close_with_pending_request_clears_it(command, silent_port):
    dispatcher = SnmpDispatcher()
    community = CommunityData("public", mpModel=1)
    transport = await UdpTransportTarget.create(
        ("127.0.0.1", silent_port), timeout=5.0, retries=0
    )
    oid = ObjectType(ObjectIdentity("1.3.6.1.2.1.1.3.0"))
    requests = {
        "get": lambda: get_cmd(dispatcher, community, transport, oid),
        "next": lambda: next_cmd(dispatcher, community, transport, oid),
        "set": lambda: set_cmd(
            dispatcher,
            community,
            transport,
            ObjectType(ObjectIdentity("1.3.6.1.2.1.1.5.0"), OctetString("x")),
        ),
        "bulk": lambda: bulk_cmd(dispatcher, community, transport, 0, 1, oid),
        "notify": lambda: send_notification(
            dispatcher,
            community,
            transport,
            "inform",
            NotificationType(ObjectIdentity("1.3.6.1.6.3.1.1.5.2")),
        ),
    }
    task = asyncio.ensure_future(requests[command]())
    await asyncio.sleep(0.2)
    task.cancel()
    await asyncio.sleep(0)

    dispatcher.close()  # must not raise

    assert dispatcher._pendingReqs == {}
    with pytest.raises(asyncio.CancelledError):
        await task
