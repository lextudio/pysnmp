import asyncio
from datetime import datetime
import pytest
from pysnmp.hlapi.v1arch.asyncio import *
from pysnmp.proto.rfc1905 import errorStatus as pysnmp_errorStatus
from pysnmp.smi import builder, compiler, view

from tests.agent_context import AGENT_PORT, AgentContextManager


@pytest.mark.asyncio
async def test_v1_get():
    async with AgentContextManager():
        snmpDispatcher = SnmpDispatcher()

        iterator = await get_cmd(
            snmpDispatcher,
            CommunityData("public", mpModel=0),
            await UdpTransportTarget.create(("localhost", AGENT_PORT)),
            ("1.3.6.1.2.1.1.1.0", None),
        )

        errorIndication, errorStatus, errorIndex, varBinds = iterator

        assert errorIndication is None
        assert errorStatus == 0
        assert errorIndex == 0
        assert len(varBinds) == 1
        assert varBinds[0][0].prettyPrint() == "1.3.6.1.2.1.1.1.0"
        assert varBinds[0][1].prettyPrint().startswith("PySNMP engine version")

        name = pysnmp_errorStatus.namedValues.getName(errorStatus)
        assert name == "noError"

        snmpDispatcher.transport_dispatcher.close_dispatcher()


@pytest.mark.asyncio
async def test_v1_get_ipv6():
    async with AgentContextManager(enable_ipv6=True):
        snmpDispatcher = SnmpDispatcher()

        iterator = await get_cmd(
            snmpDispatcher,
            CommunityData("public", mpModel=0),
            await Udp6TransportTarget.create(("localhost", AGENT_PORT)),
            ("1.3.6.1.2.1.1.1.0", None),
        )

        errorIndication, errorStatus, errorIndex, varBinds = iterator

        assert errorIndication is None
        assert errorStatus == 0
        assert errorIndex == 0
        assert len(varBinds) == 1
        assert varBinds[0][0].prettyPrint() == "1.3.6.1.2.1.1.1.0"
        assert varBinds[0][1].prettyPrint().startswith("PySNMP engine version")

        name = pysnmp_errorStatus.namedValues.getName(errorStatus)
        assert name == "noError"

        snmpDispatcher.transport_dispatcher.close_dispatcher()


# TODO:
# def test_v1_get_timeout_invalid_target():
#     loop = asyncio.get_event_loop()
#     snmpDispatcher = SnmpDispatcher()

#     async def run_get():
#         errorIndication, errorStatus, errorIndex, varBinds = await get_cmd(
#             snmpDispatcher,
#             CommunityData("community_string"),
#             await UdpTransportTarget.create(("1.2.3.4", 161), timeout=1, retries=0),
#             ObjectType(ObjectIdentity("1.3.6.1.4.1.60069.9.1.0")),
#         )
#         for varBind in varBinds:
#             print([str(varBind[0]), varBind[1]])

#     start = datetime.now()
#     try:
#         loop.run_until_complete(asyncio.wait_for(run_get(), timeout=3))
#         end = datetime.now()
#         elapsed_time = (end - start).total_seconds()
#         assert elapsed_time >= 1 and elapsed_time <= 3
#     except asyncio.TimeoutError:
#         assert False, "Test case timed out"
#     finally:
#         snmpDispatcher.transport_dispatcher.close_dispatcher()


# @pytest.mark.asyncio
# async def test_v1_get_timeout_slow_object():
#     async with AgentContextManager(enable_custom_objects=True):
#         snmpDispatcher = SnmpDispatcher()

#         async def run_get():
#             errorIndication, errorStatus, errorIndex, varBinds = await get_cmd(
#                 snmpDispatcher,
#                 CommunityData("public", mpModel=0),
#                 await UdpTransportTarget.create(
#                     ("localhost", AGENT_PORT), timeout=1, retries=0
#                 ),
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
#             snmpDispatcher.transport_dispatcher.close_dispatcher()


@pytest.mark.asyncio
async def test_v1_get_no_access_object():
    async with AgentContextManager(enable_custom_objects=True):
        snmpDispatcher = SnmpDispatcher()
        errorIndication, errorStatus, errorIndex, varBinds = await get_cmd(
            snmpDispatcher,
            CommunityData("public", mpModel=0),
            await UdpTransportTarget.create(
                ("localhost", AGENT_PORT), timeout=1, retries=0
            ),
            ObjectType(ObjectIdentity("1.3.6.1.4.1.60069.9.3")),
        )
        assert errorIndication is None
        assert errorStatus.prettyPrint() == "noSuchName"  # v1 does not have noAccess
        snmpDispatcher.transport_dispatcher.close_dispatcher()


@pytest.mark.asyncio
async def test_v1_get_dateandtime_object():
    async with AgentContextManager(enable_custom_objects=True):
        snmpDispatcher = SnmpDispatcher()
        # Step 1: Set up MIB builder and add custom MIB directory
        mibBuilder = builder.MibBuilder()
        compiler.addMibCompiler(mibBuilder)
        mibViewController = view.MibViewController(mibBuilder)

        # Load the custom MIB
        mibBuilder.loadModules("LEXTUDIO-TEST-MIB")
        snmpDispatcher.cache["mibViewController"] = mibViewController

        errorIndication, errorStatus, errorIndex, varBinds = await get_cmd(
            snmpDispatcher,
            CommunityData("public", mpModel=0),
            await UdpTransportTarget.create(
                ("localhost", AGENT_PORT), timeout=1, retries=0
            ),
            ObjectType(
                ObjectIdentity("LEXTUDIO-TEST-MIB", "testDateAndTime", 0)
            ),  # "1.3.6.1.4.1.60069.9.5.0"
        )
        assert errorIndication is None
        assert errorIndication is None
        assert errorStatus == 0
        assert errorIndex == 0
        assert len(varBinds) == 1
        assert varBinds[0][0].prettyPrint() == "LEXTUDIO-TEST-MIB::testDateAndTime.0"
        assert (
            varBinds[0][1].prettyPrint() == "2024-11-3,19:52:40.0,+0:0"
        )  # IMPORTANT: test DateAndTime display hint.


@pytest.mark.asyncio
async def test_v1_get_physaddress_object():
    async with AgentContextManager(enable_custom_objects=True):
        snmpDispatcher = SnmpDispatcher()
        # Step 1: Set up MIB builder and add custom MIB directory
        mibBuilder = builder.MibBuilder()
        compiler.addMibCompiler(mibBuilder)
        mibViewController = view.MibViewController(mibBuilder)

        # Load the custom MIB
        mibBuilder.loadModules("LEXTUDIO-TEST-MIB")
        snmpDispatcher.cache["mibViewController"] = mibViewController

        errorIndication, errorStatus, errorIndex, varBinds = await get_cmd(
            snmpDispatcher,
            CommunityData("public", mpModel=0),
            await UdpTransportTarget.create(
                ("localhost", AGENT_PORT), timeout=1, retries=0
            ),
            ObjectType(
                ObjectIdentity("LEXTUDIO-TEST-MIB", "testPhysAddress", 0)
            ),  # "1.3.6.1.4.1.60069.9.6.0"
        )
        assert errorIndication is None
        assert errorIndication is None
        assert errorStatus == 0
        assert errorIndex == 0
        assert len(varBinds) == 1
        assert varBinds[0][0].prettyPrint() == "LEXTUDIO-TEST-MIB::testPhysAddress.0"
        assert (
            varBinds[0][1].prettyPrint() == "00:11:22:33:44:55"
        )  # IMPORTANT: test PhysAddress display hint.


@pytest.mark.asyncio
async def test_v1_get_scaled_integer_object():
    async with AgentContextManager(enable_custom_objects=True):
        snmpDispatcher = SnmpDispatcher()
        # Step 1: Set up MIB builder and add custom MIB directory
        mibBuilder = builder.MibBuilder()
        compiler.addMibCompiler(mibBuilder)
        mibViewController = view.MibViewController(mibBuilder)

        # Load the custom MIB
        mibBuilder.loadModules("LEXTUDIO-TEST-MIB")
        snmpDispatcher.cache["mibViewController"] = mibViewController

        errorIndication, errorStatus, errorIndex, varBinds = await get_cmd(
            snmpDispatcher,
            CommunityData("public", mpModel=0),
            await UdpTransportTarget.create(
                ("localhost", AGENT_PORT), timeout=1, retries=0
            ),
            ObjectType(
                ObjectIdentity("LEXTUDIO-TEST-MIB", "testScaledInteger", 0)
            ),  # "1.3.6.1.4.1.60069.9.7.0"
        )
        assert errorIndication is None
        assert errorIndication is None
        assert errorStatus == 0
        assert errorIndex == 0
        assert len(varBinds) == 1
        assert varBinds[0][0].prettyPrint() == "LEXTUDIO-TEST-MIB::testScaledInteger.0"
        assert (
            varBinds[0][1].prettyPrint() == "5.0"
        )  # IMPORTANT: test display hint "d-1".


@pytest.mark.asyncio
async def test_v1_get_scaled_unsigned_object():
    async with AgentContextManager(enable_custom_objects=True):
        snmpDispatcher = SnmpDispatcher()
        # Step 1: Set up MIB builder and add custom MIB directory
        mibBuilder = builder.MibBuilder()
        compiler.addMibCompiler(mibBuilder)
        mibViewController = view.MibViewController(mibBuilder)

        # Load the custom MIB
        mibBuilder.loadModules("LEXTUDIO-TEST-MIB")
        snmpDispatcher.cache["mibViewController"] = mibViewController

        errorIndication, errorStatus, errorIndex, varBinds = await get_cmd(
            snmpDispatcher,
            CommunityData("public", mpModel=0),
            await UdpTransportTarget.create(
                ("localhost", AGENT_PORT), timeout=1, retries=0
            ),
            ObjectType(
                ObjectIdentity("LEXTUDIO-TEST-MIB", "testScaledUnsigned", 0)
            ),  # "1.3.6.1.4.1.60069.9.8.0"
        )
        assert errorIndication is None
        assert errorIndication is None
        assert errorStatus == 0
        assert errorIndex == 0
        assert len(varBinds) == 1
        assert varBinds[0][0].prettyPrint() == "LEXTUDIO-TEST-MIB::testScaledUnsigned.0"
        assert (
            varBinds[0][1].prettyPrint() == "0.5"  # GitHub issue #139
        )  # IMPORTANT: test display hint "d-1".
