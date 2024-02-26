import pytest
from pysnmp.hlapi.v3arch.asyncio import *
from tests.agent_context import AGENT_PORT, AgentContextManager


# @pytest.mark.asyncio
# async def test_v2c_bulk():
#     async with AgentContextManager():
#         with Slim() as slim:
#             errorIndication, errorStatus, errorIndex, varBinds = await slim.bulk(
#                 "public",
#                 "localhost",
#                 AGENT_PORT,
#                 0,
#                 50,
#                 ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)),
#             )

#             assert errorIndication is None
#             assert errorStatus == 0
#             assert len(varBinds) == 50
#             assert varBinds[0][0][0].prettyPrint() == "SNMPv2-MIB::sysObjectID.0"
#             assert varBinds[0][0][1].prettyPrint() == "PYSNMP-MIB::pysnmp"
#             # assert isinstance(varBinds[0][0][1], ObjectIdentifier)


# @pytest.mark.asyncio
# async def test_v2c_get_table_bulk():
#     async with AgentContextManager():
#         snmpEngine = SnmpEngine()
#         objects = bulkWalkCmd(
#             snmpEngine,
#             CommunityData("public"),
#             UdpTransportTarget(("localhost", AGENT_PORT)),
#             ContextData(),
#             0,
#             4,
#             ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)),
#         )

#         objects_list = [item async for item in objects]

#         errorIndication, errorStatus, errorIndex, varBinds = objects_list[0]

#         assert errorIndication is None
#         assert errorStatus == 0
#         assert len(varBinds) == 1
#         assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysObjectID.0"
#         assert varBinds[0][1].prettyPrint() == "PYSNMP-MIB::pysnmp"
#         # assert isinstance(varBinds[0][1], ObjectIdentifier)

#         errorIndication, errorStatus, errorIndex, varBinds = objects_list[1]

#         assert errorIndication is None
#         assert errorStatus == 0
#         assert len(varBinds) == 1
#         assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysUpTime.0"
#         # assert isinstance(varBinds[0][1], TimeTicks)

#         assert len(objects_list), 50

#         snmpEngine.transportDispatcher.closeDispatcher()
