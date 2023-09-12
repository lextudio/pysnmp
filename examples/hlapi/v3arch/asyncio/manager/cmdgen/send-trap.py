import asyncio
from pysnmp.hlapi.asyncio import *

async def run():
    snmpEngine = SnmpEngine()
    # Example of how you might update sysUpTime
    mibBuilder = snmpEngine.msgAndPduDsp.mibInstrumController.mibBuilder
    sysUpTime, = mibBuilder.importSymbols('__SNMPv2-MIB', 'sysUpTime')
    sysUpTime.syntax = TimeTicks(12345)  # Set uptime to 12345

    errorIndication, errorStatus, errorIndex, varBinds = await sendNotification(
        snmpEngine,
        CommunityData('public', mpModel=0),
        UdpTransportTarget(('demo.pysnmp.com', 162)),
        ContextData(),
        "trap",
        NotificationType(ObjectIdentity('NET-SNMP-EXAMPLES-MIB', 'netSnmpExampleNotification')).addVarBinds(ObjectType(ObjectIdentity('NET-SNMP-EXAMPLES-MIB','netSnmpExampleHeartbeatRate'), 1))
    )

    if errorIndication:
        print(errorIndication)

    snmpEngine.transportDispatcher.closeDispatcher()


asyncio.run(run())