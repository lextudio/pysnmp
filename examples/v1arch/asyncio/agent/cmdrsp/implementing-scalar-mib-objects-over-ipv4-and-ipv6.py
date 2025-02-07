"""
Implementing scalar MIB objects
+++++++++++++++++++++++++++++++

Listen and respond to SNMP GET/GETNEXT queries with the following options:

* SNMPv1 or SNMPv2c
* with SNMP community "public"
* over IPv4/UDP, listening at 127.0.0.1:161
* over IPv6/UDP, listening at [::1]:161
* serving two Managed Objects Instances (sysDescr.0 and sysUptime.0)

Either of the following Net-SNMP commands will walk this Agent:

| $ snmpwalk -v2c -c public 127.0.0.1 .1.3.6
| $ snmpwalk -v2c -c public udp6:[::1] .1.3.6

The Command Receiver below uses two distinct transports for communication
with Command Generators - UDP over IPv4 and UDP over IPv6.

"""  #
from pysnmp.carrier.asyncio.dispatch import AsyncioDispatcher
from pysnmp.carrier.asyncio.dgram import udp, udp6
from pyasn1.codec.ber import encoder, decoder
from pysnmp.proto import api
import time, bisect


class SysDescr:
    name = (1, 3, 6, 1, 2, 1, 1, 1, 0)

    def __eq__(self, other):
        return self.name == other

    def __ne__(self, other):
        return self.name != other

    def __lt__(self, other):
        return self.name < other

    def __le__(self, other):
        return self.name <= other

    def __gt__(self, other):
        return self.name > other

    def __ge__(self, other):
        return self.name >= other

    def __call__(self, protoVer):
        return api.PROTOCOL_MODULES[protoVer].OctetString(
            "PySNMP example command responder"
        )


class Uptime:
    name = (1, 3, 6, 1, 2, 1, 1, 3, 0)
    birthday = time.time()

    def __eq__(self, other):
        return self.name == other

    def __ne__(self, other):
        return self.name != other

    def __lt__(self, other):
        return self.name < other

    def __le__(self, other):
        return self.name <= other

    def __gt__(self, other):
        return self.name > other

    def __ge__(self, other):
        return self.name >= other

    def __call__(self, protoVer):
        return api.PROTOCOL_MODULES[protoVer].TimeTicks(
            (time.time() - self.birthday) * 100
        )


mibInstr = (SysDescr(), Uptime())  # sorted by object name

mibInstrIdx = {}
for mibVar in mibInstr:
    mibInstrIdx[mibVar.name] = mibVar


def __callback(transportDispatcher, transportDomain, transportAddress, wholeMsg):
    while wholeMsg:
        msgVer = api.decodeMessageVersion(wholeMsg)
        if msgVer in api.PROTOCOL_MODULES:
            pMod = api.PROTOCOL_MODULES[msgVer]
        else:
            print("Unsupported SNMP version %s" % msgVer)
            return
        reqMsg, wholeMsg = decoder.decode(
            wholeMsg,
            asn1Spec=pMod.Message(),
        )
        rspMsg = pMod.apiMessage.get_response(reqMsg)
        rspPDU = pMod.apiMessage.get_pdu(rspMsg)
        reqPDU = pMod.apiMessage.get_pdu(reqMsg)
        varBinds = []
        pendingErrors = []
        errorIndex = 0
        # GETNEXT PDU
        if reqPDU.isSameTypeWith(pMod.GetNextRequestPDU()):
            # Produce response var-binds
            for oid, val in pMod.apiPDU.get_varbinds(reqPDU):
                errorIndex = errorIndex + 1
                # Search next OID to report
                nextIdx = bisect.bisect(mibInstr, oid)
                if nextIdx == len(mibInstr):
                    # Out of MIB
                    varBinds.append((oid, val))
                    pendingErrors.append((pMod.apiPDU.set_end_of_mib_error, errorIndex))
                else:
                    # Report value if OID is found
                    varBinds.append((mibInstr[nextIdx].name, mibInstr[nextIdx](msgVer)))
        elif reqPDU.isSameTypeWith(pMod.GetRequestPDU()):
            for oid, val in pMod.apiPDU.get_varbinds(reqPDU):
                if oid in mibInstrIdx:
                    varBinds.append((oid, mibInstrIdx[oid](msgVer)))
                else:
                    # No such instance
                    varBinds.append((oid, val))
                    pendingErrors.append(
                        (pMod.apiPDU.set_no_such_instance_error, errorIndex)
                    )
                    break
        else:
            # Report unsupported request type
            pMod.apiPDU.set_error_status(rspPDU, "genErr")
        pMod.apiPDU.set_varbinds(rspPDU, varBinds)
        # Commit possible error indices to response PDU
        for f, i in pendingErrors:
            f(rspPDU, i)
        transportDispatcher.send_message(
            encoder.encode(rspMsg), transportDomain, transportAddress
        )
    return wholeMsg


transportDispatcher = AsyncioDispatcher()
transportDispatcher.register_recv_callback(__callback)

# UDP/IPv4
transportDispatcher.register_transport(
    udp.DOMAIN_NAME, udp.UdpAsyncioTransport().open_server_mode(("localhost", 161))
)

# UDP/IPv6
transportDispatcher.register_transport(
    udp6.DOMAIN_NAME, udp6.Udp6AsyncioTransport().open_server_mode(("::1", 161))
)

transportDispatcher.job_started(1)

try:
    print("This program needs to run as root/administrator to monitor port 161.")
    print("Started. Press Ctrl-C to stop")
    # Dispatcher will never finish as job#1 never reaches zero
    transportDispatcher.run_dispatcher()

except KeyboardInterrupt:
    print("Shutting down...")

finally:
    transportDispatcher.close_dispatcher()
