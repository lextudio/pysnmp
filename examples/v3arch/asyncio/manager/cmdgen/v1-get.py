"""
SNMPv1
++++++

* with SNMPv1, community 'public'
* over IPv4/UDP
* to an Agent at 127.0.0.1:161
* for an OID in tuple form

This script performs similar to the following Net-SNMP command:

| $ snmpget -v1 -c public -ObentU 127.0.0.1 1.3.6.1.2.1.1.1.0

"""  #
from pysnmp.entity import engine, config
from pysnmp.carrier.asyncio.dgram import udp
from pysnmp.entity.rfc3413 import cmdgen

# Create SNMP engine instance
snmpEngine = engine.SnmpEngine()

#
# SNMPv1 setup
#

# SecurityName <-> CommunityName mapping
config.add_v1_system(snmpEngine, "my-area", "public")

# Specify security settings per SecurityName (SNMPv1 - 0, SNMPv2c - 1)
config.add_target_parameters(snmpEngine, "my-creds", "my-area", "noAuthNoPriv", 0)

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
    varBinds,
    cbCtx,
):
    if errorIndication:
        print(errorIndication)
    # SNMPv1 response may contain noSuchName error *and* SNMPv2c exception,
    # so we ignore noSuchName error here
    elif errorStatus and errorStatus != 2:
        print(
            f"{errorStatus.prettyPrint()} at {varBinds[int(errorIndex) - 1][0] if errorIndex else '?'}"
        )
    else:
        for oid, val in varBinds:
            print(f"{oid.prettyPrint()} = {val.prettyPrint()}")


# Prepare and send a request message
cmdgen.GetCommandGenerator().send_varbinds(
    snmpEngine,
    "my-router",
    None,
    "",  # contextEngineId, contextName
    [((1, 3, 6, 1, 2, 1, 1, 1, 0), None)],
    cbFun,
)

# Run I/O dispatcher which would send pending queries and process responses
snmpEngine.open_dispatcher(3)

snmpEngine.close_dispatcher()
