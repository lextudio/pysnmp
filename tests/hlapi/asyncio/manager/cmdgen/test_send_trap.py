import pytest
from pysnmp.hlapi.v3arch.asyncio import *


@pytest.mark.asyncio
async def test_send_trap():
    snmpEngine = SnmpEngine()
    mibBuilder = snmpEngine.msgAndPduDsp.mibInstrumController.mibBuilder
    (sysUpTime,) = mibBuilder.importSymbols("__SNMPv2-MIB", "sysUpTime")
    sysUpTime.syntax = TimeTicks(12345)

    errorIndication, errorStatus, errorIndex, varBinds = await (await sendNotification(
        snmpEngine,
        CommunityData("public", mpModel=0),
        UdpTransportTarget(("demo.pysnmp.com", 162)),
        ContextData(),
        "trap",
        NotificationType(
            ObjectIdentity("NET-SNMP-EXAMPLES-MIB", "netSnmpExampleNotification")
        ).addVarBinds(
            ObjectType(
                ObjectIdentity("NET-SNMP-EXAMPLES-MIB", "netSnmpExampleHeartbeatRate"),
                1,
            )
        ),
    ))

    assert errorIndication is None
    assert errorStatus == 0
    assert len(varBinds) == 0

    snmpEngine.transportDispatcher.closeDispatcher()
