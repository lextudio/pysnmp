"""
Sequential queries
++++++++++++++++++

Send multiple SNMP GET requests one by one using the following options:

* with SNMPv2c, community 'public'
* over IPv4/UDP
* to multiple Agents at demo.pysnmp.com
* for instance of SNMPv2-MIB::sysDescr.0 MIB object
* based on asyncio I/O framework

Functionally similar to:

| $ snmpget -v2c -c public demo.pysnmp.com:161 SNMPv2-MIB::sysDescr.0
| $ snmpget -v2c -c public demo.pysnmp.com:161 SNMPv2-MIB::sysDescr.0
| $ snmpget -v2c -c public demo.pysnmp.com:161 SNMPv2-MIB::sysDescr.0

"""  #

import asyncio
from pysnmp.hlapi.v1arch.asyncio import *


async def getone(snmpDispatcher, hostname):
    iterator = await get_cmd(
        snmpDispatcher,
        CommunityData("public"),
        await UdpTransportTarget.create(hostname),
        ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)),
    )

    errorIndication, errorStatus, errorIndex, varBinds = iterator

    if errorIndication:
        print(errorIndication)

    elif errorStatus:
        print(
            "{} at {}".format(
                errorStatus.prettyPrint(),
                errorIndex and varBinds[int(errorIndex) - 1][0] or "?",
            )
        )
    else:
        for varBind in varBinds:
            print(" = ".join([x.prettyPrint() for x in varBind]))


async def getall(snmpDispatcher, hostnames):
    for hostname in hostnames:
        await getone(snmpDispatcher, hostname)


with SnmpDispatcher() as snmpDispatcher:
    asyncio.run(
        getall(
            snmpDispatcher,
            [
                ("demo.pysnmp.com", 161),
                ("demo.pysnmp.com", 161),
                ("demo.pysnmp.com", 161),
            ],
        )
    )
