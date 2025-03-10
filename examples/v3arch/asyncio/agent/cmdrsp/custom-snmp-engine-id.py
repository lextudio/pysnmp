"""
Specific SNMP Engine ID
+++++++++++++++++++++++

Listen and respond to SNMP GET/SET/GETNEXT/GETBULK queries with
the following options:

* SNMPv3
* with SNMP EngineID: 8000000004030201
* with USM user 'usr-md5-des', auth: MD5, priv DES
* allow access to SNMPv2-MIB objects (1.3.6.1.2.1)
* over IPv4/UDP, listening at 127.0.0.1:161

The following Net-SNMP command will walk this Agent:

| $ snmpwalk -v3 -u usr-md5-des -l authPriv -A authkey1 -X privkey1 -e 8000000004030201 localhost .1.3.6

"""  #
from pysnmp.entity import engine, config
from pysnmp.entity.rfc3413 import cmdrsp, context
from pysnmp.carrier.asyncio.dgram import udp
from pysnmp.proto import rfc1902

# Create SNMP engine
snmpEngine = engine.SnmpEngine(rfc1902.OctetString(hexValue="8000000004030201"))

# Transport setup

# UDP over IPv4
config.add_transport(
    snmpEngine, udp.DOMAIN_NAME, udp.UdpTransport().open_server_mode(("127.0.0.1", 161))
)

# SNMPv3/USM setup

# user: usr-md5-des, auth: MD5, priv DES
config.add_v3_user(
    snmpEngine,
    "usr-md5-des",
    config.USM_AUTH_HMAC96_MD5,
    "authkey1",
    config.USM_PRIV_CBC56_DES,
    "privkey1",
)

# Allow full MIB access for each user at VACM
config.add_vacm_user(
    snmpEngine, 3, "usr-md5-des", "authPriv", (1, 3, 6, 1, 2, 1), (1, 3, 6, 1, 2, 1)
)

# Get default SNMP context this SNMP engine serves
snmpContext = context.SnmpContext(snmpEngine)

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
