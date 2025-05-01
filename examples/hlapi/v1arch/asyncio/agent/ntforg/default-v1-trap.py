"""
SNMPv1 TRAP with defaults
+++++++++++++++++++++++++

Send SNMPv1 TRAP using the following options:

* SNMPv1
* with community name 'public'
* over IPv4/UDP
* send TRAP notification
* with Generic Trap #1 (warmStart) and Specific Trap 0
* with default Uptime
* with default Agent Address
* with Enterprise OID 1.3.6.1.4.1.20408.4.1.1.2
* include managed object information '1.3.6.1.2.1.1.1.0' = 'my system'

Functionally similar to:

| $ snmptrap -v1 -c public demo.pysnmp.com 1.3.6.1.4.1.20408.4.1.1.2 0.0.0.0 \
        1 0 0 1.3.6.1.2.1.1.1.0 s "my system"

"""  #

import asyncio
from pysnmp.hlapi.v1arch.asyncio import *


async def run():
    with SnmpDispatcher() as snmpDispatcher:
        iterator = await send_notification(
            snmpDispatcher,
            CommunityData("public", mpModel=0),
            await UdpTransportTarget.create(("demo.pysnmp.com", 162)),
            "trap",
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


asyncio.run(run())
