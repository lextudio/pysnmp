"""
TRAP over multiple transports
+++++++++++++++++++++++++++++

The following script sends two SNMP TRAP notification using the
following options:

* with SNMPv1
* with community name 'public'
* over IPv4/UDP and IPv6/UDP
* send TRAP notification
* to a Manager at demo.pysnmp.com:162 and [::1]
* with TRAP ID 'coldStart' specified as an OID
* include managed objects information:
* with default Uptime value
* with default Agent Address with '127.0.0.1'
* overriding Enterprise OID with 1.3.6.1.4.1.20408.4.1.1.2

The following Net-SNMP commands will produce similar SNMP notification:

| $ snmptrap -v1 -c public udp:demo.pysnmp.com 1.3.6.1.4.1.20408.4.1.1.2 127.0.0.1 1 0 12345
| $ snmptrap -v1 -c public udp6:[::1] 1.3.6.1.4.1.20408.4.1.1.2 127.0.0.1 1 0 12345

"""  #
from pysnmp.carrier.asyncio.dispatch import AsyncioDispatcher
from pysnmp.carrier.asyncio.dgram import udp, udp6
from pyasn1.codec.ber import encoder
from pysnmp.proto import api

# Protocol version to use
pMod = api.PROTOCOL_MODULES[api.SNMP_VERSION_1]
# pMod = api.PROTOCOL_MODULES[api.SNMP_VERSION_2C]

# Build PDU
trapPDU = pMod.TrapPDU()
pMod.apiTrapPDU.set_defaults(trapPDU)

# Traps have quite different semantics across proto versions
if pMod == api.PROTOCOL_MODULES[api.SNMP_VERSION_1]:
    pMod.apiTrapPDU.set_enterprise(trapPDU, (1, 3, 6, 1, 1, 2, 3, 4, 1))
    pMod.apiTrapPDU.set_generic_trap(trapPDU, "coldStart")

# Build message
trapMsg = pMod.Message()
pMod.apiMessage.set_defaults(trapMsg)
pMod.apiMessage.set_community(trapMsg, "public")
pMod.apiMessage.set_pdu(trapMsg, trapPDU)

transportDispatcher = AsyncioDispatcher()

# UDP/IPv4
transportDispatcher.register_transport(
    udp.DOMAIN_NAME, udp.UdpAsyncioTransport().open_client_mode()
)
transportDispatcher.send_message(
    encoder.encode(trapMsg), udp.DOMAIN_NAME, ("demo.pysnmp.com", 162)
)

# UDP/IPv6
transportDispatcher.register_transport(
    udp6.DOMAIN_NAME, udp6.Udp6AsyncioTransport().open_client_mode()
)
transportDispatcher.send_message(
    encoder.encode(trapMsg), udp6.DOMAIN_NAME, ("::1", 162)
)

# Dispatcher will finish as all scheduled messages are sent
transportDispatcher.run_dispatcher(3)

transportDispatcher.close_dispatcher()
