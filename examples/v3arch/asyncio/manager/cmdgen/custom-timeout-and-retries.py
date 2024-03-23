"""
SNMPv2c, custom timeout
+++++++++++++++++++++++

Send a SNMP GET request:

* with SNMPv2c, community 'public'
* over IPv4/UDP
* to an Agent at 127.0.0.1:161
* wait 3 seconds for response, retry 5 times (plus one initial attempt)
* for an OID in tuple form

This script performs similar to the following Net-SNMP command:

| $ snmpget -v2c -c public -ObentU -r 5 -t 1 127.0.0.1 1.3.6.1.2.1.1.1.0

"""  #
from pysnmp.entity import engine, config
from pysnmp.carrier.asyncio.dgram import udp
from pysnmp.entity.rfc3413 import cmdgen

# Create SNMP engine instance
snmpEngine = engine.SnmpEngine()

#
# SNMPv2c setup
#

# SecurityName <-> CommunityName mapping
config.addV1System(snmpEngine, "my-area", "public")

# Specify security settings per SecurityName (SNMPv1 - 0, SNMPv2c - 1)
config.addTargetParams(snmpEngine, "my-creds", "my-area", "noAuthNoPriv", 1)

#
# Setup transport endpoint and bind it with security settings yielding
# a target name
#

# UDP/IPv4
config.addTransport(
    snmpEngine, udp.DOMAIN_NAME, udp.UdpAsyncioTransport().openClientMode()
)

config.addTargetAddr(
    snmpEngine,
    "my-router",
    udp.DOMAIN_NAME,
    ("127.0.0.1", 161),
    "my-creds",
    timeout=300,  # in 1/100 sec
    retryCount=5,
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
cmdgen.GetCommandGenerator().sendVarBinds(
    snmpEngine,
    "my-router",
    None,
    "",  # contextEngineId, contextName
    [((1, 3, 6, 1, 2, 1, 1, 1, 0), None)],
    cbFun,
)

# Run I/O dispatcher which would send pending queries and process responses
snmpEngine.transportDispatcher.runDispatcher(3)

snmpEngine.transportDispatcher.closeDispatcher()
