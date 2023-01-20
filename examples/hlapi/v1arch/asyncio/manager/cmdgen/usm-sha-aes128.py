"""
SNMPv3: auth SHA, privacy AES128
++++++++++++++++++++++++++++++++
Send SNMP GET request using the following options:
* with SNMPv3, user 'usr-sha-aes', SHA authentication, AES128 encryption
* over IPv4/UDP
* to an Agent at demo.pysnmp.com:161
* for SNMPv2-MIB::sysDescr.0 MIB object
Available authentication protocols:
#. usmHMACMD5AuthProtocol
#. usmHMACSHAAuthProtocol
#. usmHMAC128SHA224AuthProtocol
#. usmHMAC192SHA256AuthProtocol
#. usmHMAC256SHA384AuthProtocol
#. usmHMAC384SHA512AuthProtocol
#. usmNoAuthProtocol
Available privacy protocols:
#. usmDESPrivProtocol
#. usm3DESEDEPrivProtocol
#. usmAesCfb128Protocol
#. usmAesCfb192Protocol
#. usmAesCfb256Protocol
#. usmNoPrivProtocol
Functionally similar to:
| $ snmpget -v3 -l authPriv -u usr-sha-aes -A authkey1 -X privkey1 -a SHA -x AES demo.pysnmp.com SNMPv2-MIB::sysDescr.0
"""#
import asyncio
from pysnmp.hlapi.asyncio import *

async def run():
    snmpEngine = SnmpEngine()
    get_result = await getCmd(
        snmpEngine,
        UsmUserData('usr-sha-aes', 'authkey1', 'privkey1',
                    authProtocol=usmHMACSHAAuthProtocol,
                    privProtocol=usmAesCfb128Protocol),
        UdpTransportTarget(('demo.pysnmp.com', 161)),
        ContextData(),
        ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0)))

    errorIndication, errorStatus, errorIndex, varBinds = await get_result
    if errorIndication:
        print(errorIndication)
    elif errorStatus:
        print('%s at %s' % (errorStatus.prettyPrint(),
                            errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
    else:
        for varBind in varBinds:
            print(' = '.join([x.prettyPrint() for x in varBind]))

asyncio.run(run())
