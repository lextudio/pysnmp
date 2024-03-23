import pytest
from pysnmp.hlapi.v3arch.asyncio import *
from tests.manager_context import MANAGER_PORT, ManagerContextManager


@pytest.mark.asyncio
async def test_send_v3_trap_notification():
    async with ManagerContextManager():
        snmpEngine = SnmpEngine(OctetString(hexValue="8000000001020304"))
        errorIndication, errorStatus, errorIndex, varBinds = await (await sendNotification(
            snmpEngine,
            UsmUserData("usr-md5-des", "authkey1", "privkey1"),
            UdpTransportTarget(("localhost", MANAGER_PORT)),
            ContextData(),
            "trap",
            NotificationType(ObjectIdentity("IF-MIB", "linkDown")),
        ))

        snmpEngine.transportDispatcher.closeDispatcher()
