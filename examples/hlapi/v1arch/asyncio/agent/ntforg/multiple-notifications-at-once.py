"""
Multiple concurrent notifications
+++++++++++++++++++++++++++++++++

Send multiple SNMP notifications at once using the following options:

* SNMPv2c
* with community name 'public'
* over IPv4/UDP
* send INFORM notification
* to multiple Managers
* with TRAP ID 'coldStart' specified as a MIB symbol

Functionally similar to:

| $ snmptrap -v2c -c public demo.pysnmp.com 12345 1.3.6.1.6.3.1.1.5.2
| $ snmpinform -v2c -c public demo.pysnmp.com 12345 1.3.6.1.6.3.1.1.5.2

"""  #

import asyncio
from pysnmp.hlapi.v1arch.asyncio import *


async def sendone(snmpDispatcher, hostname, notifyType):
    iterator = await send_notification(
        snmpDispatcher,
        CommunityData("public"),
        await UdpTransportTarget.create((hostname, 162)),
        notifyType,
        NotificationType(ObjectIdentity("1.3.6.1.6.3.1.1.5.2"))
        .load_mibs("SNMPv2-MIB")
        .add_varbinds(
            ("1.3.6.1.6.3.1.1.4.3.0", "1.3.6.1.4.1.20408.4.1.1.2"),
            ("1.3.6.1.2.1.1.1.0", OctetString("my system")),
        ),
    )

    errorIndication, errorStatus, errorIndex, varBinds = iterator

    if errorIndication:
        print(errorIndication)

    elif errorStatus:
        print(
            "{}: at {}".format(
                errorStatus.prettyPrint(),
                errorIndex and varBinds[int(errorIndex) - 1][0] or "?",
            )
        )

    else:
        for varBind in varBinds:
            print(" = ".join([x.prettyPrint() for x in varBind]))


async def main():
    with SnmpDispatcher() as snmpDispatcher:
        await asyncio.gather(
            sendone(snmpDispatcher, "demo.pysnmp.com", "trap"),
            sendone(snmpDispatcher, "demo.pysnmp.com", "inform"),
        )


asyncio.run(main())
