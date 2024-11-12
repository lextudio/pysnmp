import asyncio
import socket
import pytest


from pysnmp.hlapi.v3arch.asyncio import *
from tests.manager_context import MANAGER_PORT, ManagerContextManager


@pytest.mark.asyncio
async def test_send_v3_trap_notification():
    async with ManagerContextManager() as (_, message_count):
        # snmptrap -v3 -l authPriv -u usr-md5-des -A authkey1 -X privkey1 -e 8000000001020304 localhost:MANAGER_PORT 0 1.3.6.1.6.3.1.1.5.1 1.3.6.1.2.1.1.1.0 s "my system"
        snmpEngine = SnmpEngine(OctetString(hexValue="8000000001020304"))
        errorIndication, errorStatus, errorIndex, varBinds = await send_notification(
            snmpEngine,
            UsmUserData("usr-md5-des", "authkey1", "privkey1"),
            await UdpTransportTarget.create(("localhost", MANAGER_PORT)),
            ContextData(),
            "trap",
            NotificationType(ObjectIdentity("IF-MIB", "linkDown")),
        )

        snmpEngine.close_dispatcher()
        await asyncio.sleep(1)
        assert message_count == [1]


@pytest.mark.asyncio
async def test_send_v3_trap_notification_none():
    async with ManagerContextManager() as (_, message_count):
        # snmptrap -v3 -l noAuthNoPriv -u usr-none-none -e 8000000001020305 localhost:MANAGER_PORT 0 1.3.6.1.6.3.1.1.5.1 1.3.6.1.2.1.1.1.0 s "my system"
        snmpEngine = SnmpEngine(OctetString(hexValue="8000000001020305"))
        errorIndication, errorStatus, errorIndex, varBinds = await send_notification(
            snmpEngine,
            UsmUserData("usr-none-none", None, None),
            await UdpTransportTarget.create(("localhost", MANAGER_PORT)),
            ContextData(),
            "trap",
            NotificationType(ObjectIdentity("IF-MIB", "linkDown")),
        )

        snmpEngine.close_dispatcher()
        await asyncio.sleep(1)
        assert message_count == [1]


@pytest.mark.asyncio
async def test_send_v3_trap_notification_invalid_user():
    async with ManagerContextManager() as (_, message_count):
        # snmptrap -v3 -l authPriv -u usr-md5-des -A authkey1 -X privkey1 -e 8000000001020304 localhost:MANAGER_PORT 0 1.3.6.1.6.3.1.1.5.1 1.3.6.1.2.1.1.1.0 s "my system"
        snmpEngine = SnmpEngine(OctetString(hexValue="8000000001020304"))
        errorIndication, errorStatus, errorIndex, varBinds = await send_notification(
            snmpEngine,
            UsmUserData("usr-md5-des1", "authkey1", "privkey1"),
            await UdpTransportTarget.create(("localhost", MANAGER_PORT)),
            ContextData(),
            "trap",
            NotificationType(ObjectIdentity("IF-MIB", "linkDown")),
        )

        snmpEngine.close_dispatcher()
        await asyncio.sleep(1)
        assert message_count == [0]


hex_dump = """
30 81 BC 02  01 03 30 11  02 04 61 03  A8 E3 02 03
00 FF E3 04  01 03 02 01  03 04 3A 30  38 04 08 80
00 00 00 01  02 03 04 02  01 01 02 04  05 35 84 3C
04 0B 75 73  72 2D 6D 64  35 2D 64 65  73 04 0C 36
04 72 CD 9B  57 02 49 45  C2 86 F6 04  08 00 00 00
0C CB C9 9A  08 04 68 2B  7D 70 58 59  12 E1 9F CC
A7 74 AD D7  1F 89 D4 BD  6B 8A D4 93  50 E5 31 82
98 45 C5 2A  23 CA 0A D2  3B A0 CF 59  C4 96 58 D3
CC 1A 8C 8F  87 82 FC 27  E4 AC 6B 54  8A 28 B9 D3
FA CD 92 E6  62 0C FB 65  42 62 9E CE  76 34 A9 02
3C CF 3A 05  7C 1F 3C B2  D3 0E B4 2F  8A 66 CB B4
10 66 A8 F4  A9 E3 D8 3C  44 BE 28 52  AC 70 27
"""
# copied from snmptrap -d -v3 -l authPriv -u usr-md5-des -A authkey1 -X privkey1 -e 8000000001020304 localhost:1622 0 1.3.6.1.6.3.1.1.5.1 1.3.6.1.2.1.1.1.0 s "my system"


def hex_dump_to_bytes(hex_dump):
    # Split the hex dump into lines
    lines = hex_dump.strip().split("\n")

    # Extract the hex bytes from each line
    hex_bytes = []
    for line in lines:
        # Skip the beginning of the line (offset) and drop the end of the line (non-hex characters)
        hex_part = line.replace(" ", "")
        hex_bytes.append(hex_part)

    # Join all hex bytes into a single string
    hex_string = "".join(hex_bytes)

    # Convert the hex string to a byte array
    return bytes.fromhex(hex_string)


@pytest.mark.asyncio
async def test_send_v3_trap_notification_raw():
    async with ManagerContextManager() as (_, message_count):
        raw_bytes = hex_dump_to_bytes(hex_dump)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(raw_bytes, ("localhost", MANAGER_PORT))
        await asyncio.sleep(1)
        assert message_count == [1]


@pytest.mark.asyncio
async def test_send_v3_trap_notification_invalid_msg_flags():
    async with ManagerContextManager() as (_, message_count):
        raw_bytes = bytearray(hex_dump_to_bytes(hex_dump))
        assert raw_bytes[21] == 0x03  # check the original value
        raw_bytes[
            21
        ] = 0x02  # manually changed line 2, "04  01 03" to "04  01 02" to make the message invalid
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(raw_bytes, ("localhost", MANAGER_PORT))
        await asyncio.sleep(1)
        assert message_count == [0]
