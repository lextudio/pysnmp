"""
Sequential queries
++++++++++++++++++

Send multiple SNMP GET requests one by one using the following options:

* with SNMPv2c, community 'public'
* over IPv4/UDP
* to multiple Agents at localhost
* for instance of SNMPv2-MIB::sysDescr.0 MIB object
* based on asyncio I/O framework

Functionally similar to:

| $ snmpget -v2c -c public localhost:1161 SNMPv2-MIB::sysDescr.0
| $ snmpget -v2c -c public localhost:2161 SNMPv2-MIB::sysDescr.0
| $ snmpget -v2c -c public localhost:3161 SNMPv2-MIB::sysDescr.0

"""#
import asyncio
from pysnmp.hlapi.v3arch.asyncio import *


async def getone(snmpEngine, hostname):
    errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
        snmpEngine,
        CommunityData('public'),
        UdpTransportTarget(hostname),
        ContextData(),
        ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0))
    )

    if errorIndication:
        print(errorIndication)

    elif errorStatus:
        print('%s at %s' % (
            errorStatus.prettyPrint(),
            errorIndex and varBinds[int(errorIndex) - 1][0] or '?'
        )
              )
    else:
        for varBind in varBinds:
            print(' = '.join([x.prettyPrint() for x in varBind]))


async def getall(snmpEngine, hostnames):
    for hostname in hostnames:
        await getone(snmpEngine, hostname)


snmpEngine = SnmpEngine()

asyncio.run(getall(snmpEngine, [('localhost', 161),
                                            ('localhost', 162),
                                            ('localhost', 163)]))
