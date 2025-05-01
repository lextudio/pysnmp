"""
SNMPv1
++++++

Send SNMP GET request using the following options:

  * with SNMPv1, community 'public'
  * over IPv4/UDP
  * to an Agent at demo.pysnmp.com:161
  * for the 1.3.6.1.2.1.1.1.0 OID (e.g. SNMPv2-MIB::sysDescr.0 MIB object)
  * Based on asyncio I/O framework

Functionally similar to:

| $ snmpget -v1 -c public demo.pysnmp.com SNMPv2-MIB::sysDescr.0

"""  #

import asyncio
from pysnmp.hlapi.v1arch.asyncio import *


async def run():
    with SnmpDispatcher() as snmpDispatcher:
        iterator = await get_cmd(
            snmpDispatcher,
            CommunityData("public", mpModel=0),
            await UdpTransportTarget.create(("demo.pysnmp.com", 161)),
            ("1.3.6.1.2.1.1.1.0", None),
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


asyncio.run(run())
