"""
INFORM over multiple transports
+++++++++++++++++++++++++++++++

The following script sends SNMP INFORM notification using the following options:

* with SNMPv2c
* with community name 'public'
* over IPv4/UDP and IPv6/UDP
* send INFORM notification
* to a Manager at demo.pysnmp.com:162 and [::1]:162
* with TRAP ID 'coldStart' specified as an OID

The following Net-SNMP command will produce similar SNMP notification:

| $ snmpinform -v2c -c public udp:demo.pysnmp.com 0 1.3.6.1.6.3.1.1.5.1
| $ snmpinform -v2c -c public udp6:[::1] 0 1.3.6.1.6.3.1.1.5.1

"""#
from pysnmp.carrier.asyncio.dispatch import AsyncioDispatcher
from pysnmp.carrier.asyncio.dgram import udp, udp6
from pyasn1.codec.ber import encoder, decoder
from pysnmp.proto.api import v2c as pMod

# Build PDU
reqPDU = pMod.InformRequestPDU()
pMod.apiTrapPDU.setDefaults(reqPDU)

# Build message
trapMsg = pMod.Message()
pMod.apiMessage.setDefaults(trapMsg)
pMod.apiMessage.setCommunity(trapMsg, 'public')
pMod.apiMessage.setPDU(trapMsg, reqPDU)

# noinspection PyUnusedLocal,PyUnusedLocal
def cbRecvFun(
    transportDispatcher, transportDomain, transportAddress, wholeMsg, reqPDU=reqPDU
):
    while wholeMsg:
        rspMsg, wholeMsg = decoder.decode(wholeMsg, asn1Spec=pMod.Message())
        rspPDU = pMod.apiMessage.getPDU(rspMsg)

        # Match response to request
        if pMod.apiPDU.getRequestID(reqPDU) == pMod.apiPDU.getRequestID(rspPDU):

            # Check for SNMP errors reported
            errorStatus = pMod.apiPDU.getErrorStatus(rspPDU)
            if errorStatus:
                print(errorStatus.prettyPrint())

            else:
                print('INFORM message delivered, response var-binds follow')

                for oid, val in pMod.apiPDU.getVarBinds(rspPDU):
                    print('%s = %s' % (oid.prettyPrint(), val.prettyPrint()))

            transportDispatcher.jobFinished(1)

    return wholeMsg


transportDispatcher = AsyncioDispatcher()

transportDispatcher.registerRecvCbFun(cbRecvFun)

# UDP/IPv4
transportDispatcher.registerTransport(
    udp.DOMAIN_NAME, udp.UdpAsyncioTransport().openClientMode()
)
transportDispatcher.sendMessage(
    encoder.encode(trapMsg), udp.DOMAIN_NAME, ('demo.pysnmp.com', 162)
)
transportDispatcher.jobStarted(1)

# UDP/IPv6
# transportDispatcher.registerTransport(
#    udp6.domainName, udp6.Udp6AsyncioTransport().openClientMode()
# )
# transportDispatcher.sendMessage(
#    encoder.encode(trapMsg), udp6.domainName, ('::1', 162)
# )
# transportDispatcher.jobStarted(1)

# Dispatcher will finish as all scheduled messages are sent
transportDispatcher.runDispatcher(3)

transportDispatcher.closeDispatcher()
