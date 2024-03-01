import asyncio
from datetime import datetime
import pytest
from pysnmp.hlapi.v3arch.asyncio import *
from tests.agent_context import AGENT_PORT, AgentContextManager


# @pytest.mark.asyncio
# async def test_v1_get():
#     async with AgentContextManager():
#         with Slim(1) as slim:
#             errorIndication, errorStatus, errorIndex, varBinds = await slim.get(
#                 "public",
#                 "localhost",
#                 AGENT_PORT,
#                 ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)),
#             )

#             assert errorIndication is None
#             assert errorStatus == 0
#             assert errorIndex == 0
#             assert len(varBinds) == 1
#             assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysDescr.0"
#             assert varBinds[0][1].prettyPrint().startswith("PySNMP engine version")
#             assert isinstance(varBinds[0][1], OctetString)


@pytest.mark.asyncio
async def test_v1_get_old():
    async with AgentContextManager():
        slim = Slim(1)
        errorIndication, errorStatus, errorIndex, varBinds = await slim.get(
            "public",
            "localhost",
            AGENT_PORT,
            ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)),
        )

        assert errorIndication is None
        assert errorStatus == 0
        assert errorIndex == 0
        assert len(varBinds) == 1
        assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysDescr.0"
        assert varBinds[0][1].prettyPrint().startswith("PySNMP engine version")
        assert isinstance(varBinds[0][1], OctetString)

        slim.close()


@pytest.mark.asyncio
async def test_v1_get_raw():
    async with AgentContextManager():
        snmpEngine = SnmpEngine()
        errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
            snmpEngine,
            CommunityData("public", mpModel=0),
            UdpTransportTarget(("localhost", AGENT_PORT)),
            ContextData(),
            ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)),
        )

        assert errorIndication is None
        assert errorStatus == 0
        assert len(varBinds) == 1
        assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysDescr.0"
        assert varBinds[0][1].prettyPrint().startswith("PySNMP engine version")
        assert isinstance(varBinds[0][1], OctetString)

        snmpEngine.transportDispatcher.closeDispatcher()


# @pytest.mark.asyncio
# async def test_v1_get_ipv6():
#     async with AgentContextManager(enable_ipv6=True):
#         snmpEngine = SnmpEngine()
#         errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
#             snmpEngine,
#             CommunityData("public", mpModel=0),
#             Udp6TransportTarget(("localhost", AGENT_PORT)),
#             ContextData(),
#             ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)),
#         )

#         assert errorIndication is None
#         assert errorStatus == 0
#         assert len(varBinds) == 1
#         assert varBinds[0][0].prettyPrint() == 'SNMPv2-MIB::sysDescr.0'
#         assert isinstance(varBinds[0][1], OctetString)

#         snmpEngine.transportDispatcher.closeDispatcher()
