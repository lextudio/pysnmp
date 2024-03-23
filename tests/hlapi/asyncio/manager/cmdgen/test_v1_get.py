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


# @pytest.mark.asyncio
# async def test_v1_get_old():
#     async with AgentContextManager():
#         slim = Slim(1)
#         errorIndication, errorStatus, errorIndex, varBinds = await slim.get(
#             "public",
#             "localhost",
#             AGENT_PORT,
#             ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)),
#         )

#         assert errorIndication is None
#         assert errorStatus == 0
#         assert errorIndex == 0
#         assert len(varBinds) == 1
#         assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysDescr.0"
#         assert varBinds[0][1].prettyPrint().startswith("PySNMP engine version")
#         assert isinstance(varBinds[0][1], OctetString)

#         slim.close()


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


@pytest.mark.asyncio
async def test_v1_get_ipv6():
    async with AgentContextManager(enable_ipv6=True):
        snmpEngine = SnmpEngine()
        errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
            snmpEngine,
            CommunityData("public", mpModel=0),
            Udp6TransportTarget(("localhost", AGENT_PORT)),
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


def test_v1_get_timeout_invalid_target():
    loop = asyncio.get_event_loop()
    snmpEngine = SnmpEngine()

    async def run_get():
        errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
            snmpEngine,
            CommunityData("community_string"),
            UdpTransportTarget(("1.2.3.4", 161), timeout=1, retries=0),
            ContextData(),
            ObjectType(ObjectIdentity("1.3.6.1.4.1.60069.9.1.0")),
        )
        for varBind in varBinds:
            print([str(varBind[0]), varBind[1]])

    start = datetime.now()
    try:
        loop.run_until_complete(asyncio.wait_for(run_get(), timeout=3))
        end = datetime.now()
        elapsed_time = (end - start).total_seconds()
        assert elapsed_time >= 1 and elapsed_time <= 3
    except asyncio.TimeoutError:
        assert False, "Test case timed out"
    finally:
        snmpEngine.transportDispatcher.closeDispatcher()


# @pytest.mark.asyncio
# async def test_v1_get_timeout_slow_object():
#     async with AgentContextManager(enable_slow_object=True):
#         snmpEngine = SnmpEngine()

#         async def run_get():
#             errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
#                 snmpEngine,
#                 CommunityData("public", mpModel=0),
#                 UdpTransportTarget(("localhost", AGENT_PORT), timeout=1, retries=0),
#                 ContextData(),
#                 ObjectType(ObjectIdentity("1.3.6.1.4.1.60069.9.1.0")),
#             )
#             for varBind in varBinds:
#                 print([str(varBind[0]), varBind[1]])

#         start = datetime.now()
#         try:
#             await asyncio.wait_for(run_get(), timeout=3)
#             end = datetime.now()
#             elapsed_time = (end - start).total_seconds()
#             assert elapsed_time >= 1 and elapsed_time <= 3
#         except asyncio.TimeoutError:
#             assert False, "Test case timed out"
#         finally:
#             snmpEngine.transportDispatcher.closeDispatcher()
