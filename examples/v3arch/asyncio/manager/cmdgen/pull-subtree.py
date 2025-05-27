"""
Pull MIB subtree
++++++++++++++++

Send a series of SNMP GETNEXT requests
* with SNMPv3 with user 'usr-none-none', no auth and no privacy protocols
* over IPv4/UDP
* to an Agent at 127.0.0.1:161
* for an OID in string form
* stop whenever received OID goes out of initial prefix (it may be a table)

This script performs similar to the following Net-SNMP command:

| $ snmpwalk -v3 -l noAuthNoPriv -u usr-none-none -ObentU 127.0.0.1:161  1.3.6.1.2.1.1

"""  #

from pysnmp.entity import engine, config
from pysnmp.carrier.asyncio.dgram import udp
from pysnmp.entity.rfc3413 import cmdgen
from pysnmp.proto import rfc1902

# Initial OID prefix
initialOID = rfc1902.ObjectName("1.3.6.1.2.1.1")

# Create SNMP engine instance
snmpEngine = engine.SnmpEngine()

#
# SNMPv3/USM setup
#

# user: usr-none-none, auth: none, priv: none
config.add_v3_user(
    snmpEngine,
    "usr-none-none",
)
config.add_target_parameters(snmpEngine, "my-creds", "usr-none-none", "noAuthNoPriv")

#
# Setup transport endpoint and bind it with security settings yielding
# a target name
#

# UDP/IPv4
config.add_transport(
    snmpEngine, udp.DOMAIN_NAME, udp.UdpAsyncioTransport().open_client_mode()
)
config.add_target_address(
    snmpEngine, "my-router", udp.DOMAIN_NAME, ("127.0.0.1", 161), "my-creds"
)


# Error/response receiver
# noinspection PyUnusedLocal,PyUnusedLocal,PyUnusedLocal
def cbFun(
    snmpEngine,
    sendRequestHandle,
    errorIndication,
    errorStatus,
    errorIndex,
    varBindTable,
    cbCtx,
):
    if errorIndication:
        print(errorIndication)
        return
    if errorStatus:
        print(
            f"{errorStatus.prettyPrint()} at {varBindTable[-1][int(errorIndex) - 1][0] if errorIndex else '?'}"
        )
        return  # stop on error
    for varBindRow in varBindTable:
        for oid, val in varBindRow:
            if initialOID.isPrefixOf(oid):
                print(f"{oid.prettyPrint()} = {val.prettyPrint()}")
            else:
                return False  # signal dispatcher to stop
    return True  # signal dispatcher to continue


# Prepare initial request to be sent
cmdgen.NextCommandGenerator().send_varbinds(
    snmpEngine,
    "my-router",
    None,
    "",  # contextEngineId, contextName
    [(initialOID, None)],
    cbFun,
)

# Run I/O dispatcher which would send pending queries and process responses
snmpEngine.open_dispatcher(3)

snmpEngine.close_dispatcher()
