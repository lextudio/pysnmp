"""
Set scalar value
++++++++++++++++

Send a SNMP SET request
* with SNMPv2c with community name 'private'
* over IPv4/UDP
* to an Agent at 127.0.0.1:161
* for an OID in tuple form and an integer-typed value

This script performs similar to the following Net-SNMP command:

| $ snmpset -v2c -c private -ObentU 127.0.0.1:161 1.3.6.1.2.1.1.9.1.4.1 t 123

"""  #

from pysnmp.entity import engine, config
from pysnmp.carrier.asyncio.dgram import udp
from pysnmp.entity.rfc3413 import cmdgen
from pysnmp.proto import rfc1902

# Create SNMP engine instance
snmpEngine = engine.SnmpEngine()

#
# SNMPv2c setup
#

# SecurityName <-> CommunityName mapping
config.add_v1_system(snmpEngine, "my-area", "private")

# Specify security settings per SecurityName (SNMPv1 - 0, SNMPv2c - 1)
config.add_target_parameters(snmpEngine, "my-creds", "my-area", "noAuthNoPriv", 1)

#
# Setup transport endpoint and bind it with security settings yielding
# a target name
#

# UDP/IPv4
config.add_transport(snmpEngine, udp.DOMAIN_NAME, udp.UdpTransport().open_client_mode())
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
    varBinds,
    cbCtx,
):
    if errorIndication:
        print(errorIndication)
    elif errorStatus:
        print(
            f"{errorStatus.prettyPrint()} at {varBinds[int(errorIndex) - 1][0] if errorIndex else '?'}"
        )
    else:
        for oid, val in varBinds:
            print(f"{oid.prettyPrint()} = {val.prettyPrint()}")


# Prepare and send a request message
cmdgen.SetCommandGenerator().send_varbinds(
    snmpEngine,
    "my-router",
    None,
    "",  # contextEngineId, contextName
    [((1, 3, 6, 1, 2, 1, 1, 9, 1, 4, 1), rfc1902.TimeTicks(123))],
    cbFun,
)

# Run I/O dispatcher which would send pending queries and process responses
snmpEngine.open_dispatcher(3)

snmpEngine.close_dispatcher()
