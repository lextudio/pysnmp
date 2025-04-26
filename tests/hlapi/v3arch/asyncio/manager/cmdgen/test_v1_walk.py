import pytest
from pysnmp.hlapi.v3arch.asyncio import *
from pysnmp.smi.builder import MibBuilder
from pysnmp.smi.view import MibViewController
from tests.agent_context import AGENT_PORT, AgentContextManager

total_count = 212  # 267


@pytest.mark.asyncio
async def test_v1_walk():
    async with AgentContextManager():
        with SnmpEngine() as snmpEngine:
            objects = walk_cmd(
                snmpEngine,
                CommunityData("public", mpModel=0),
                await UdpTransportTarget.create(("localhost", AGENT_PORT)),
                ContextData(),
                ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)),
            )

            objects_list = [item async for item in objects]

            errorIndication, errorStatus, errorIndex, varBinds = objects_list[0]

            assert errorIndication is None
            assert errorStatus == 0
            assert len(varBinds) == 1
            assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysObjectID.0"

            errorIndication, errorStatus, errorIndex, varBinds = objects_list[1]

            assert errorIndication is None
            assert errorStatus == 0
            assert len(varBinds) == 1
            assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysUpTime.0"

            assert len(objects_list) == total_count


@pytest.mark.asyncio
async def test_v1_walk_mib():
    async with AgentContextManager():
        mib_builder = MibBuilder()
        mib_view_controller = MibViewController(mib_builder)
        mib_builder.load_modules(
            "SNMP-COMMUNITY-MIB",
            "PYSNMP-MIB",
            "PYSNMP-USM-MIB",
            "SNMP-VIEW-BASED-ACM-MIB",
        )

        with SnmpEngine() as snmpEngine:
            snmpEngine.cache["mibViewController"] = mib_view_controller
            objects = walk_cmd(
                snmpEngine,
                CommunityData("public", mpModel=0),
                await UdpTransportTarget.create(("localhost", AGENT_PORT)),
                ContextData(),
                ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)),
            )

            objects_list = [item async for item in objects]

            errorIndication, errorStatus, errorIndex, varBinds = objects_list[0]

            assert errorIndication is None
            assert errorStatus == 0
            assert len(varBinds) == 1
            assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysObjectID.0"

            errorIndication, errorStatus, errorIndex, varBinds = objects_list[1]

            assert errorIndication is None
            assert errorStatus == 0
            assert len(varBinds) == 1
            assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysUpTime.0"

            assert len(objects_list) == total_count

            errorIndication, errorStatus, errorIndex, varBinds = objects_list[-1]
            assert (
                varBinds[0][0].prettyPrint()
                == 'SNMP-COMMUNITY-MIB::snmpCommunityStatus."public"'
            )

            for errorIndication, errorStatus, errorIndex, varBinds in objects_list:
                content = varBinds[0][0].prettyPrint()
                if (
                    not content.startswith("PYSNMP-USM-MIB::")
                    and not content.startswith("SNMP-USER-BASED-SM-MIB::")
                    and not content.startswith("SNMP-VIEW-BASED-ACM-MIB::")
                ):
                    assert content.count(".") == 1  # fully resolved.


@pytest.mark.asyncio
async def test_v1_walk_subtree():
    async with AgentContextManager():
        with SnmpEngine() as snmpEngine:
            objects = walk_cmd(
                snmpEngine,
                CommunityData("public", mpModel=0),
                await UdpTransportTarget.create(("localhost", AGENT_PORT)),
                ContextData(),
                ObjectType(ObjectIdentity("SNMPv2-MIB", "system")),
                lexicographicMode=False,
            )

            objects_list = [item async for item in objects]

            errorIndication, errorStatus, errorIndex, varBinds = objects_list[0]

            assert errorIndication is None
            assert errorStatus == 0
            assert len(varBinds) == 1
            assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysDescr.0"

            errorIndication, errorStatus, errorIndex, varBinds = objects_list[1]

            assert errorIndication is None
            assert errorStatus == 0
            assert len(varBinds) == 1
            assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysObjectID.0"

            assert len(objects_list) == 8
