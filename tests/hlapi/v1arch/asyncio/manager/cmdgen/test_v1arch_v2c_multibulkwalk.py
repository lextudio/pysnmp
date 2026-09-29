import pytest

from pysnmp.proto.errind import RequestTimedOut
from pysnmp.hlapi.v1arch.asyncio import *
from tests.agent_context import AGENT_PORT, AgentContextManager


@pytest.mark.asyncio
async def test_v2c_multi_bulk_walk_multiple_subtrees():
    """
    Test that multi_bulk_walk_cmd can walk multiple OID trees in parallel
    and complete independently.
    """
    async with AgentContextManager():
        with SnmpDispatcher() as snmpDispatcher:
            max_repetitions = 2
            objects = multi_bulk_walk_cmd(
                snmpDispatcher,
                CommunityData("public"),
                await UdpTransportTarget.create(("localhost", AGENT_PORT)),
                0,
                max_repetitions,
                ObjectType(ObjectIdentity("SNMPv2-MIB", "system")),
                ObjectType(ObjectIdentity("SNMPv2-MIB", "snmp")),
                maxRows=20,
                lexicographicMode=False,
            )

            count = 0
            seen_system = False
            seen_snmp = False
            async for errorIndication, errorStatus, errorIndex, varBinds in objects:
                assert errorIndication is None
                assert errorStatus == 0
                assert isinstance(varBinds, tuple)
                assert len(varBinds) > 0
                for vb in varBinds:
                    name = vb[0].prettyPrint()
                    if name.startswith("SNMPv2-MIB::sys"):
                        seen_system = True
                    if name.startswith("SNMPv2-MIB::snmp"):
                        seen_snmp = True
                count += 1

            assert seen_system and seen_snmp
            assert count > 0


@pytest.mark.asyncio
async def test_v2c_multi_bulk_walk_lookupmib_false():
    async with AgentContextManager():
        with SnmpDispatcher() as snmpDispatcher:
            count = 0
            max_repetitions = 2
            objects = multi_bulk_walk_cmd(
                snmpDispatcher,
                CommunityData("public"),
                await UdpTransportTarget.create(("localhost", AGENT_PORT)),
                0,
                max_repetitions,
                ObjectType(ObjectIdentity("SNMPv2-MIB", "system")),
                ObjectType(ObjectIdentity("SNMPv2-MIB", "snmp")),
                lookupMib=False,
                lexicographicMode=False,
            )

            async for errorIndication, errorStatus, errorIndex, varBinds in objects:
                assert errorIndication is None
                assert errorStatus == 0
                assert isinstance(varBinds, tuple)
                count += 1
                if count >= 5:
                    break

            assert count >= 3


@pytest.mark.asyncio
async def test_v2c_multi_bulk_walk_lookupmib_true():
    async with AgentContextManager():
        with SnmpDispatcher() as snmpDispatcher:
            count = 0
            max_repetitions = 1
            objects = multi_bulk_walk_cmd(
                snmpDispatcher,
                CommunityData("public"),
                await UdpTransportTarget.create(("localhost", AGENT_PORT)),
                0,
                max_repetitions,
                ObjectType(ObjectIdentity("SNMPv2-MIB", "system")),
                ObjectType(ObjectIdentity("SNMPv2-MIB", "snmp")),
                lookupMib=True,
            )

            async for errorIndication, errorStatus, errorIndex, varBinds in objects:
                assert errorIndication is None
                assert errorStatus == 0
                count += 1
                if count > 5:
                    break

            assert count > 0


@pytest.mark.asyncio
async def test_v2c_multi_bulk_walk_maxrows_limit():
    max_rows = 6
    async with AgentContextManager():
        with SnmpDispatcher() as snmpDispatcher:
            total_seen = 0
            max_repetitions = 2
            objects = multi_bulk_walk_cmd(
                snmpDispatcher,
                CommunityData("public"),
                await UdpTransportTarget.create(("localhost", AGENT_PORT)),
                0,
                max_repetitions,
                ObjectType(ObjectIdentity("SNMPv2-MIB", "system")),
                ObjectType(ObjectIdentity("SNMPv2-MIB", "snmp")),
                lexicographicMode=False,
                maxRows=max_rows,
            )

            async for errorIndication, errorStatus, errorIndex, varBinds in objects:
                assert errorIndication is None
                assert errorStatus == 0
                total_seen += len(varBinds)

            assert total_seen == max_rows


@pytest.mark.asyncio
async def test_v2c_multi_bulk_walk_maxcalls_limit():
    async with AgentContextManager():
        with SnmpDispatcher() as snmpDispatcher:
            max_calls = 2
            call_count = 0
            max_repetitions = 4
            objects = multi_bulk_walk_cmd(
                snmpDispatcher,
                CommunityData("public"),
                await UdpTransportTarget.create(("localhost", AGENT_PORT)),
                0,
                max_repetitions,
                ObjectType(ObjectIdentity("SNMPv2-MIB", "system")),
                ObjectType(ObjectIdentity("SNMPv2-MIB", "snmp")),
                maxCalls=max_calls,
                lexicographicMode=False,
            )

            async for errorIndication, errorStatus, errorIndex, varBinds in objects:
                call_count += 1

            assert call_count <= max_calls


@pytest.mark.asyncio
async def test_v2c_multi_bulk_walk_maxcalls_with_maxrows_varbinds_count_limit():
    async with AgentContextManager():
        with SnmpDispatcher() as snmpDispatcher:
            max_calls = 2
            max_rows = 10
            call_count = 0
            total_count = 0
            max_repetitions = 10

            objects = multi_bulk_walk_cmd(
                snmpDispatcher,
                CommunityData("public"),
                await UdpTransportTarget.create(("localhost", AGENT_PORT)),
                0,
                max_repetitions,
                ObjectType(ObjectIdentity("SNMPv2-MIB", "system")),
                ObjectType(ObjectIdentity("SNMPv2-MIB", "snmp")),
                maxCalls=max_calls,
                maxRows=max_rows,
            )

            async for errorIndication, errorStatus, errorIndex, varBinds in objects:
                total_count += len(varBinds)
                call_count += 1

            assert total_count == max_rows
            assert call_count <= max_calls


@pytest.mark.asyncio
async def test_v2c_multi_bulk_walk_ignore_non_increasing_oid():
    async with AgentContextManager():
        with SnmpDispatcher() as snmpDispatcher:
            max_repetitions = 2

            objects = multi_bulk_walk_cmd(
                snmpDispatcher,
                CommunityData("public"),
                await UdpTransportTarget.create(("localhost", AGENT_PORT)),
                0,
                max_repetitions,
                ObjectType(ObjectIdentity("SNMPv2-MIB", "system")),
                ObjectType(ObjectIdentity("SNMPv2-MIB", "snmp")),
                ignoreNonIncreasingOid=True,
            )

            count = 0
            async for errorIndication, errorStatus, errorIndex, varBinds in objects:
                assert errorStatus == 0
                count += 1
                if count > 3:
                    break

            assert count > 0


@pytest.mark.asyncio
async def test_v2c_multi_bulk_walk_0_4_subtree():
    async with AgentContextManager():
        with SnmpDispatcher() as snmpDispatcher:
            index = 0
            max_repetitions = 4
            async for (
                errorIndication,
                errorStatus,
                errorIndex,
                varBinds,
            ) in multi_bulk_walk_cmd(
                snmpDispatcher,
                CommunityData("public"),
                await UdpTransportTarget.create(("localhost", AGENT_PORT)),
                0,
                max_repetitions,
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

            assert index > 0
