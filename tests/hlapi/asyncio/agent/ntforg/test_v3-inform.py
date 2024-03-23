import pytest
from pysnmp.hlapi.v3arch.asyncio import *

from tests.manager_context import MANAGER_PORT, ManagerContextManager


@pytest.mark.asyncio
async def test_send_v3_inform():
    async with ManagerContextManager():
        snmpEngine = SnmpEngine()
        errorIndication, errorStatus, errorIndex, varBinds = await (await sendNotification(
            snmpEngine,
            UsmUserData("usr-md5-des", "authkey1", "privkey1"),
            UdpTransportTarget(("localhost", MANAGER_PORT)),
            ContextData(),
            "inform",
            NotificationType(ObjectIdentity("1.3.6.1.6.3.1.1.5.2")).addVarBinds(
                ("1.3.6.1.2.1.1.1.0", OctetString("my system"))
            ),
        ))

        assert errorIndication is None
        assert errorStatus == 0
        assert errorIndex == 0
        assert len(varBinds) == 3
        assert varBinds[0][0].prettyPrint() == "SNMPv2-SMI::mib-2.1.3.0"
        # assert varBinds[1][0].prettyPrint() == "SNMPv2-MIB::snmpTrapOID.0"
        # assert varBinds[2][0].prettyPrint() == "SNMPv2-MIB::sysDescr.0"
        isinstance(varBinds[0][1], TimeTicks)
        isinstance(varBinds[1][1], ObjectIdentifier)
        isinstance(varBinds[2][1], OctetString)
        snmpEngine.transportDispatcher.closeDispatcher()
