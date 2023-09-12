import pytest
from pysnmp.hlapi.v3arch.asyncio import *
from pysnmp.proto.api import v2c
from tests.manager_context import MANAGER_PORT, ManagerContextManager


@pytest.mark.asyncio
async def test_send_trap_enterprise_specific():
    async with ManagerContextManager():
        snmpEngine = SnmpEngine()
        errorIndication, errorStatus, errorIndex, varBinds = await sendNotification(
            snmpEngine,
            CommunityData("public", mpModel=0),
            # UdpTransportTarget(("localhost", MANAGER_PORT)), # TODO: Fix this
            UdpTransportTarget(("demo.pysnmp.com", 162)),
            ContextData(),
            "trap",
            NotificationType(
                ObjectIdentity("1.3.6.1.4.1.20408.4.1.1.2.432")
            ).addVarBinds(
                (v2c.apiTrapPDU.sysUpTime, TimeTicks(12345)),
                ("1.3.6.1.2.1.1.1.0", OctetString("my system")),
                (v2c.apiTrapPDU.snmpTrapAddress, IpAddress("127.0.0.1")),
            ),
        )
        assert errorIndication is None
        assert errorStatus == 0
        assert errorIndex == 0
        assert varBinds == []
        snmpEngine.transportDispatcher.closeDispatcher()


# @pytest.mark.asyncio
# async def test_send_trap_generic():
#     async with ManagerContextManager():
#         snmpEngine = SnmpEngine()
#         errorIndication, errorStatus, errorIndex, varBinds = await sendNotification(
#             snmpEngine,
#             CommunityData("public", mpModel=0),
#             # UdpTransportTarget(("localhost", MANAGER_PORT)), # TODO: Fix this
#             UdpTransportTarget(("demo.pysnmp.com", 162)),
#             ContextData(),
#             "trap",
#             NotificationType(ObjectIdentity("1.3.6.1.6.3.1.1.5.2")).addVarBinds(
#                 ("1.3.6.1.6.3.1.1.4.3.0", "1.3.6.1.4.1.20408.4.1.1.2"),
#                 ("1.3.6.1.2.1.1.1.0", OctetString("my system")),
#             ),
#         )
#         assert errorIndication is None
#         assert errorStatus == 0
#         assert errorIndex == 0
#         assert varBinds == []
#         snmpEngine.transportDispatcher.closeDispatcher()
