"""
Serve non-default MIB tree
++++++++++++++++++++++++++

Listen and respond to SNMP GET/SET/GETNEXT/GETBULK queries with
the following options:

* SNMPv3
* with USM username usr-md5-none
* using alternative set of Managed Objects addressed by
  contextEngineId: 8000000001020304, contextName: my-context
* allow access to SNMPv2-MIB objects (1.3.6.1.2.1)
* over IPv4/UDP, listening at 127.0.0.1:161

Either of the following Net-SNMP commands will walk this Agent:

| $ snmpwalk -v3 -u usr-md5-none -l authNoPriv -A authkey1 -E 8000000001020304 -n my-context 127.0.0.1 .1.3.6
| $ snmpwalk -v3 -u usr-md5-none -l authNoPriv -A authkey1 -E 8000000001020304 127.0.0.1 .1.3.6

"""  #
from pysnmp.entity import engine, config
from pysnmp.entity.rfc3413 import cmdrsp, context
from pysnmp.carrier.asyncio.dgram import udp
from pysnmp.smi import instrum, builder
from pysnmp.proto.api import v2c

# Create SNMP engine
snmpEngine = engine.SnmpEngine()

# Transport setup

# UDP over IPv4
config.add_transport(
    snmpEngine, udp.DOMAIN_NAME, udp.UdpTransport().open_server_mode(("127.0.0.1", 161))
)

# SNMPv3/USM setup

# user: usr-md5-none, auth: MD5, priv NONE
config.add_v3_user(snmpEngine, "usr-md5-none", config.USM_AUTH_HMAC96_MD5, "authkey1")

# Allow full MIB access for each user at VACM
config.add_vacm_user(
    snmpEngine, 3, "usr-md5-none", "authNoPriv", (1, 3, 6, 1, 2, 1), (1, 3, 6, 1, 2, 1)
)

# Create an SNMP context with ContextEngineId = 8000000001020304
snmpContext = context.SnmpContext(
    snmpEngine, contextEngineId=v2c.OctetString(hexValue="8000000001020304")
)

# Create an [empty] set of Managed Objects (MibBuilder), pass it to
# Management Instrumentation Controller and register at SNMP Context
# under ContextName 'my-context'
snmpContext.register_context_name(
    v2c.OctetString("my-context"),  # Context Name
    instrum.MibInstrumController(builder.MibBuilder()),  # Managed Objects
)

# Register SNMP Applications at the SNMP engine for particular SNMP context
cmdrsp.GetCommandResponder(snmpEngine, snmpContext)
cmdrsp.SetCommandResponder(snmpEngine, snmpContext)
cmdrsp.NextCommandResponder(snmpEngine, snmpContext)
cmdrsp.BulkCommandResponder(snmpEngine, snmpContext)

# Register an imaginary never-ending job to keep I/O dispatcher running forever
snmpEngine.transport_dispatcher.job_started(1)

# Run I/O dispatcher which would receive queries and send responses
try:
    snmpEngine.open_dispatcher()
except:
    snmpEngine.close_dispatcher()
    raise
