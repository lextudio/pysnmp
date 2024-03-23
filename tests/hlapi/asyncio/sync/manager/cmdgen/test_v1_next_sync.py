# def test_v1_next_sync():
#     snmpEngine = SnmpEngine()
#     errorIndication, errorStatus, errorIndex, varBinds = nextCmdSync(
#         snmpEngine,
#         CommunityData("public", mpModel=0),
#         UdpTransportTarget(("demo.pysnmp.com", 161)),
#         ContextData(),
#         ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)),
#     )

#     assert errorIndication is None
#     assert errorStatus == 0
#     assert len(varBinds) == 1
#     assert varBinds[0][0][0].prettyPrint() == "SNMPv2-MIB::sysObjectID.0"
#     assert varBinds[0][0][1].prettyPrint() == "SNMPv2-SMI::internet"
#     # assert isinstance(varBinds[0][0][1], ObjectIdentifier) # TODO: fix this

#     snmpEngine.transportDispatcher.closeDispatcher()
