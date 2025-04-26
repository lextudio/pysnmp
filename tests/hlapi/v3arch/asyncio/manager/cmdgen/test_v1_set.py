import pytest
from pysnmp.hlapi.v3arch.asyncio import *
from tests.agent_context import AGENT_PORT, AgentContextManager


@pytest.mark.asyncio
async def test_v1_set():
    async with AgentContextManager():
        snmpEngine = SnmpEngine()
        errorIndication, errorStatus, errorIndex, varBinds = await set_cmd(
            snmpEngine,
            CommunityData("public", mpModel=0),
            await UdpTransportTarget.create(("localhost", AGENT_PORT)),
            ContextData(),
            ObjectType(ObjectIdentity("SNMPv2-MIB", "sysLocation", 0), "Shanghai"),
        )

        assert errorIndication is None
        assert errorStatus == 0
        assert len(varBinds) == 1
        assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysLocation.0"
        assert varBinds[0][1].prettyPrint() == "Shanghai"
        assert isinstance(varBinds[0][1], OctetString)

        snmpEngine.close_dispatcher()


@pytest.mark.asyncio
async def test_v1_set_table_creation():
    async with AgentContextManager(enable_table_creation=True):
        snmpEngine = SnmpEngine()

        # Perform a SNMP walk to get all object counts
        objects = walk_cmd(
            snmpEngine,
            CommunityData("public", mpModel=0),
            await UdpTransportTarget.create(("localhost", AGENT_PORT)),
            ContextData(),
            ObjectType(ObjectIdentity("1.3.6")),
        )

        objects_list = [item async for item in objects]
        assert len(objects_list) > 0

        object_counts = len(objects_list)

        errorIndication, errorStatus, errorIndex, varBinds = await set_cmd(
            snmpEngine,
            CommunityData("public", mpModel=0),
            await UdpTransportTarget.create(("localhost", AGENT_PORT)),
            ContextData(),
            ObjectType(
                ObjectIdentity("1.3.6.6.1.5.2.97.98.99"), OctetString("My value")
            ),
        )

        assert errorIndication is None
        assert errorStatus == 0
        assert len(varBinds) == 1
        assert varBinds[0][0].prettyPrint() == "SNMPv2-SMI::dod.6.1.5.2.97.98.99"
        assert varBinds[0][1].prettyPrint() == "My value"
        assert isinstance(varBinds[0][1], OctetString)

        errorIndication, errorStatus, errorIndex, varBinds = await set_cmd(
            snmpEngine,
            CommunityData("public", mpModel=0),
            await UdpTransportTarget.create(("localhost", AGENT_PORT)),
            ContextData(),
            ObjectType(ObjectIdentity("1.3.6.6.1.5.4.97.98.99"), Integer(4)),
        )

        assert errorIndication is None
        assert errorStatus == 0
        assert len(varBinds) == 1
        assert varBinds[0][0].prettyPrint() == "SNMPv2-SMI::dod.6.1.5.4.97.98.99"
        assert varBinds[0][1].prettyPrint() == "1"
        # assert isinstance(varBinds[0][1], Integer)

        # Perform a SNMP walk to get all object counts
        objects = walk_cmd(
            snmpEngine,
            CommunityData("public", mpModel=0),
            await UdpTransportTarget.create(("localhost", AGENT_PORT)),
            ContextData(),
            ObjectType(ObjectIdentity("1.3.6")),
        )

        objects_list = [item async for item in objects]
        assert len(objects_list) > 0

        assert len(objects_list) == object_counts + 4
        snmpEngine.close_dispatcher()
