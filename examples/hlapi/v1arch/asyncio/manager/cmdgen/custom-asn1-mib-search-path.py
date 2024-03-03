"""
Custom ASN.1 MIB path
+++++++++++++++++++++

Send SNMP GET request using the following options:

* with SNMPv2c, community 'public'
* over IPv4/UDP
* to an Agent at demo.pysnmp.com:161
* for IF-MIB::ifInOctets.1 MIB object
* pass non-default ASN.1 MIB source to MIB compiler

Functionally similar to:

| $ snmpget -v2c -c public -M /usr/share/snmp demo.pysnmp.com IF-MIB::ifInOctets.1

"""  #
import asyncio
from pysnmp.hlapi.asyncio import *


async def run():
    snmpEngine = SnmpEngine()
    errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
        snmpEngine,
        CommunityData("public"),
        UdpTransportTarget(("demo.pysnmp.com", 161)),
        ContextData(),
        ObjectType(
            ObjectIdentity("IF-MIB", "ifInOctets", 1).addAsn1MibSource(
                "file:///usr/share/snmp", "https://mibs.pysnmp.com/asn1/@mib@"
            )
        ),
    )

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


asyncio.run(run())
