from pysnmp.entity.engine import SnmpEngine
from pysnmp.hlapi import *
from pysnmp.proto.rfc1902 import OctetString
from pysnmp.smi.rfc1902 import ObjectIdentity, ObjectType


# def test_v1_get():
#     with Slim(1) as slim:
#         errorIndication, errorStatus, errorIndex, varBinds = slim.get(
#             "public",
#             "demo.pysnmp.com",
#             161,
#             ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)),
#         )

#         assert errorIndication is None
#         assert errorStatus == 0
#         assert len(varBinds) == 1
#         assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysDescr.0"
#         assert varBinds[0][1].prettyPrint() == "#SNMP Agent on .NET Standard"
#         assert isinstance(varBinds[0][1], OctetString)


# def test_v1_get_raw():
#     snmpEngine = SnmpEngine()
#     errorIndication, errorStatus, errorIndex, varBinds = next(
#         getCmd(
#             snmpEngine,
#             CommunityData("public", mpModel=0),
#             UdpTransportTarget(("demo.pysnmp.com", 161)),
#             ContextData(),
#             ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)),
#         )
#     )

#     assert errorIndication is None
#     assert errorStatus == 0
#     assert len(varBinds) == 1
#     assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysDescr.0"
#     assert varBinds[0][1].prettyPrint() == "#SNMP Agent on .NET Standard"
#     assert isinstance(varBinds[0][1], OctetString)

#     snmpEngine.transportDispatcher.closeDispatcher()
