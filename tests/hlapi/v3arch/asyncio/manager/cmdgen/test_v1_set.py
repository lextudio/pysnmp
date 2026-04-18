import pytest
from pysnmp.hlapi.v3arch.asyncio import (
    CommunityData,
    ContextData,
    SnmpEngine,
    set_cmd,
    UdpTransportTarget,
    walk_cmd,
)
from pysnmp.proto.api.v1 import OctetString
from pysnmp.proto.rfc1902 import Integer32
from pysnmp.smi.rfc1902 import ObjectIdentity, ObjectType
from tests.agent_context import AGENT_PORT, AgentContextManager


@pytest.mark.asyncio
async def test_v1_set():
    async with AgentContextManager():
        with SnmpEngine() as snmpEngine:
            errorIndication, errorStatus, errorIndex, varBinds = await set_cmd(
                snmpEngine,
                CommunityData("public", mpModel=0),
                await UdpTransportTarget.create(("localhost", AGENT_PORT)),
                ContextData(),
                ObjectType(
                    ObjectIdentity("SNMPv2-MIB", "sysLocation", 0),
                    OctetString("Shanghai"),
                ),
            )

            assert errorIndication is None
            assert errorStatus == 0
            assert len(varBinds) == 1
            assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysLocation.0"
            assert varBinds[0][1].prettyPrint() == "Shanghai"
            assert isinstance(varBinds[0][1], OctetString)


@pytest.mark.asyncio
async def test_v1_set_nonexistent_oid_returns_no_such_name():
    """Test that SNMPv1 SET to non-existent OID returns noSuchName error (issue #230)."""
    async with AgentContextManager():
        with SnmpEngine() as snmpEngine:
            errorIndication, errorStatus, errorIndex, varBinds = await set_cmd(
                snmpEngine,
                CommunityData("public", mpModel=0),
                await UdpTransportTarget.create(("localhost", AGENT_PORT)),
                ContextData(),
                ObjectType(ObjectIdentity("1.3.6.1.4.1.60069.9.99.0"), Integer32(42)),
            )

            assert errorIndication is None
            # SNMPv1 wire format maps notWritable to noSuchName
            assert errorStatus.prettyPrint() == "noSuchName"


@pytest.mark.asyncio
async def test_v1_set_table_creation():
    async with AgentContextManager(enable_table_creation=True):
        with SnmpEngine() as snmpEngine:
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
                ObjectType(ObjectIdentity("1.3.6.6.1.5.4.97.98.99"), Integer32(4)),
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
