import math
import pytest

from pysnmp.hlapi.v1arch.asyncio import *
from tests.agent_context import AGENT_PORT, AgentContextManager

total_count = 68


@pytest.mark.asyncio
@pytest.mark.parametrize("max_repetitions", [1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 30])
async def test_v2c_get_table_bulk(max_repetitions):
    async with AgentContextManager():
        with SnmpDispatcher() as snmpDispatcher:
            objects = bulk_walk_cmd(
                snmpDispatcher,
                CommunityData("public"),
                # await UdpTransportTarget.create(("localhost", AGENT_PORT)),
                await UdpTransportTarget.create(("demo.pysnmp.com", 161)),
                0,
                max_repetitions,
                ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)),
            )

            objects_list = [obj async for obj in objects]

            errorIndication, errorStatus, errorIndex, varBinds = objects_list[0]

            assert errorIndication is None
            assert errorStatus == 0
            assert len(varBinds) == max_repetitions
            assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysObjectID.0"

            errorIndication, errorStatus, errorIndex, varBinds = objects_list[1]

            assert errorIndication is None
            assert errorStatus == 0
            assert len(varBinds) == max_repetitions
            # assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysName.0"

            assert len(objects_list) == math.ceil(total_count / max_repetitions)


@pytest.mark.asyncio
async def test_v2c_get_table_bulk_0_4_subtree():
    async with AgentContextManager():
        with SnmpDispatcher() as snmpDispatcher:
            index = 0
            async for (
                errorIndication,
                errorStatus,
                errorIndex,
                varBinds,
            ) in bulk_walk_cmd(
                snmpDispatcher,
                CommunityData("public"),
                await UdpTransportTarget.create(("localhost", AGENT_PORT)),
                0,
                4,
                ObjectType(ObjectIdentity("SNMPv2-MIB", "snmp")),
                lexicographicMode=False,
            ):
                assert errorIndication is None
                assert errorStatus == 0
                assert len(varBinds) == 4
                if index == 0:
                    assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::snmpInPkts.0"

                if index == 1:
                    assert (
                        varBinds[0][0].prettyPrint()
                        == "SNMPv2-MIB::snmpInBadCommunityUses.0"
                    )

                if index == 26:
                    assert (
                        varBinds[0][0].prettyPrint() == "SNMPv2-MIB::snmpSilentDrops.0"
                    )

                if index == 27:
                    assert (
                        varBinds[0][0].prettyPrint() == "SNMPv2-MIB::snmpProxyDrops.0"
                    )

                index += 1

            assert index == 7


@pytest.mark.asyncio
async def test_v2c_get_table_bulk_0_1_subtree():
    async with AgentContextManager():
        with SnmpDispatcher() as snmpDispatcher:
            index = 0
            async for (
                errorIndication,
                errorStatus,
                errorIndex,
                varBinds,
            ) in bulk_walk_cmd(
                snmpDispatcher,
                CommunityData("public"),
                await UdpTransportTarget.create(("localhost", AGENT_PORT)),
                0,
                1,
                ObjectType(ObjectIdentity("SNMPv2-MIB", "snmp")),
                lexicographicMode=False,
            ):
                assert errorIndication is None
                assert errorStatus == 0
                assert len(varBinds) == 1
                if index == 0:
                    assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::snmpInPkts.0"

                if index == 1:
                    assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::snmpOutPkts.0"

                if index == 26:
                    assert (
                        varBinds[0][0].prettyPrint() == "SNMPv2-MIB::snmpSilentDrops.0"
                    )

                if index == 27:
                    assert (
                        varBinds[0][0].prettyPrint() == "SNMPv2-MIB::snmpProxyDrops.0"
                    )

                index += 1

            assert index == 28


@pytest.mark.asyncio
async def test_v2c_get_table_bulk_0_7():
    async with AgentContextManager():
        with SnmpDispatcher() as snmpDispatcher:
            max_repetitions = 7
            objects = bulk_walk_cmd(
                snmpDispatcher,
                CommunityData("public"),
                # await UdpTransportTarget.create(("localhost", AGENT_PORT)),
                await UdpTransportTarget.create(("demo.pysnmp.com", 161)),
                0,
                max_repetitions,
                ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)),
            )

            objects_list = [obj async for obj in objects]

            errorIndication, errorStatus, errorIndex, varBinds = objects_list[0]

            assert errorIndication is None
            assert errorStatus == 0
            assert len(varBinds) == max_repetitions
            assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysObjectID.0"

            errorIndication, errorStatus, errorIndex, varBinds = objects_list[1]

            assert errorIndication is None
            assert errorStatus == 0
            assert len(varBinds) == max_repetitions
            # assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysName.0"

            assert len(objects_list) == math.ceil(total_count / max_repetitions)


@pytest.mark.asyncio
async def test_v2c_get_table_bulk_0_8():
    with SnmpDispatcher() as snmpDispatcher:
        max_repetitions = 8
        objects = bulk_walk_cmd(
            snmpDispatcher,
            CommunityData("public"),
            # await UdpTransportTarget.create(("localhost", AGENT_PORT)),
            await UdpTransportTarget.create(("demo.pysnmp.com", 161)),
            0,
            max_repetitions,
            ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)),
        )

        objects_list = [obj async for obj in objects]

        errorIndication, errorStatus, errorIndex, varBinds = objects_list[0]

        assert errorIndication is None
        assert errorStatus == 0
        assert len(varBinds) == max_repetitions
        assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysObjectID.0"

        errorIndication, errorStatus, errorIndex, varBinds = objects_list[1]

        assert errorIndication is None
        assert errorStatus == 0
        assert len(varBinds) == max_repetitions
        # assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysName.0"

        assert len(objects_list) == math.ceil(total_count / max_repetitions)


@pytest.mark.asyncio
async def test_v2c_get_table_bulk_0_35():
    async with AgentContextManager():
        with SnmpDispatcher() as snmpDispatcher:
            max_repetitions = 35  # 68/2 + 1
            objects = bulk_walk_cmd(
                snmpDispatcher,
                CommunityData("public"),
                # await UdpTransportTarget.create(("localhost", AGENT_PORT)),
                await UdpTransportTarget.create(("demo.pysnmp.com", 161)),
                0,
                max_repetitions,
                ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)),
            )

            objects_list = [obj async for obj in objects]

            errorIndication, errorStatus, errorIndex, varBinds = objects_list[0]

            assert errorIndication is None
            assert errorStatus == 0
            assert len(varBinds) == max_repetitions
            assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysObjectID.0"

            errorIndication, errorStatus, errorIndex, varBinds = objects_list[1]

            assert errorIndication is None
            assert errorStatus == 0
            assert len(varBinds) == total_count - max_repetitions
            # assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysName.0"

            assert len(objects_list) == math.ceil(total_count / max_repetitions)


@pytest.mark.asyncio
async def test_v2c_get_table_bulk_0_60():
    async with AgentContextManager():
        with SnmpDispatcher() as snmpDispatcher:
            max_repetitions = 60
            objects = bulk_walk_cmd(
                snmpDispatcher,
                CommunityData("public"),
                # await UdpTransportTarget.create(("localhost", AGENT_PORT)),
                await UdpTransportTarget.create(("demo.pysnmp.com", 161)),
                0,
                max_repetitions,
                ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)),
            )

            objects_list = [obj async for obj in objects]

            errorIndication, errorStatus, errorIndex, varBinds = objects_list[0]

            assert errorIndication is None
            assert errorStatus == 0
            assert len(varBinds) == max_repetitions
            assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysObjectID.0"

            assert len(objects_list) == math.ceil(total_count / max_repetitions)


@pytest.mark.asyncio
async def test_v2c_get_table_bulk_0_5_subtree():
    async with AgentContextManager():
        with SnmpDispatcher() as snmpDispatcher:
            max_repetitions = 5
            objects = bulk_walk_cmd(
                snmpDispatcher,
                CommunityData("public"),
                # await UdpTransportTarget.create(("localhost", AGENT_PORT)),
                await UdpTransportTarget.create(("demo.pysnmp.com", 161)),
                0,
                max_repetitions,
                ObjectType(ObjectIdentity("SNMPv2-MIB", "system")),
                lexicographicMode=False,
            )

            objects_list = [obj async for obj in objects]

            errorIndication, errorStatus, errorIndex, varBinds = objects_list[0]

            assert errorIndication is None
            assert errorStatus == 0
            assert len(varBinds) == max_repetitions
            assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysDescr.0"

            errorIndication, errorStatus, errorIndex, varBinds = objects_list[3]
            assert len(varBinds) == 1

            assert len(objects_list) == 4


@pytest.mark.asyncio
async def test_v2c_get_table_bulk_0_6_subtree():
    async with AgentContextManager():
        with SnmpDispatcher() as snmpDispatcher:
            max_repetitions = 6
            objects = bulk_walk_cmd(
                snmpDispatcher,
                CommunityData("public"),
                # await UdpTransportTarget.create(("localhost", AGENT_PORT)),
                await UdpTransportTarget.create(("demo.pysnmp.com", 161)),
                0,
                max_repetitions,
                ObjectType(ObjectIdentity("SNMPv2-MIB", "system")),
                lexicographicMode=False,
            )

            objects_list = [obj async for obj in objects]

            errorIndication, errorStatus, errorIndex, varBinds = objects_list[0]

            assert errorIndication is None
            assert errorStatus == 0
            assert len(varBinds) == max_repetitions
            assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysDescr.0"

            errorIndication, errorStatus, errorIndex, varBinds = objects_list[2]
            assert len(varBinds) == 4

            assert len(objects_list) == 3


@pytest.mark.asyncio
async def test_bulk_walk_lookupmib_true():
    """
    Test that bulk_walk_cmd() works correctly with lookupMib=True.
    This tests the default behavior.
    """
    async with AgentContextManager():
        with SnmpDispatcher() as snmpDispatcher:
            count = 0
            objects = bulk_walk_cmd(
                snmpDispatcher,
                CommunityData("public"),
                await UdpTransportTarget.create(("localhost", AGENT_PORT)),
                0,
                1,  # Small max_repetitions to ensure multiple queries
                ObjectType(ObjectIdentity("SNMPv2-MIB", "system")),
                lookupMib=True,
            )

            # This should work fine
            async for errorIndication, errorStatus, errorIndex, varBinds in objects:
                assert errorIndication is None, (
                    f"Error with lookupMib=True: {errorIndication}"
                )
                count += 1
                if count >= 5:  # Process at least some responses
                    break

            assert count > 0, "No lookupMib=True responses processed"


@pytest.mark.asyncio
async def test_bulk_walk_lookupmib_false():
    """
    Test that bulk_walk_cmd() works correctly with lookupMib=False.

    Previously this might have failed because when lookupMib=False, the unmake_varbinds() helper
    function returns plain ObjectName objects instead of ObjectIdentity objects,
    which would cause a type mismatch when creating the next query.

    This test confirms the v1arch implementation correctly handles lookupMib=False.
    """
    async with AgentContextManager():
        with SnmpDispatcher() as snmpDispatcher:
            count = 0

            objects = bulk_walk_cmd(
                snmpDispatcher,
                CommunityData("public"),
                await UdpTransportTarget.create(("localhost", AGENT_PORT)),
                0,
                1,  # Small max_repetitions to ensure multiple queries
                ObjectType(ObjectIdentity("SNMPv2-MIB", "system")),
                lookupMib=False,
            )

            # This should work correctly
            async for errorIndication, errorStatus, errorIndex, varBinds in objects:
                assert errorIndication is None, (
                    f"Error with lookupMib=False: {errorIndication}"
                )
                count += 1
                if count >= 5:  # Process at least some responses to confirm it works
                    break

            # We should be able to process multiple responses without error
            assert count > 0, "No responses processed with lookupMib=False"
            assert count >= 2, "Expected multiple responses with lookupMib=False"
