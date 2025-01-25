import pytest
from pysnmp.entity.engine import SnmpEngine
from pysnmp.hlapi.v1arch.asyncio.cmdgen import get_cmd, set_cmd, walk_cmd
from pysnmp.hlapi.v1arch.asyncio.dispatch import SnmpDispatcher
from pysnmp.hlapi.v1arch.asyncio.transport import UdpTransportTarget
from pysnmp.hlapi.v1arch.asyncio.auth import CommunityData
from pysnmp.proto.rfc1902 import Integer, OctetString
from pysnmp.smi import builder, compiler, view
from pysnmp.smi.rfc1902 import ObjectIdentity, ObjectType
from tests.agent_context import AGENT_PORT, AgentContextManager


@pytest.mark.asyncio
async def test_v1_set():
    async with AgentContextManager():
        snmpDispatcher = SnmpDispatcher()

        iterator = await set_cmd(
            snmpDispatcher,
            CommunityData("public", mpModel=0),
            await UdpTransportTarget.create(("localhost", AGENT_PORT)),
            ObjectType(ObjectIdentity("SNMPv2-MIB", "sysLocation", 0), "Shanghai"),
        )

        errorIndication, errorStatus, errorIndex, varBinds = iterator

        assert errorIndication is None
        assert errorStatus == 0
        assert len(varBinds) == 1
        assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysLocation.0"
        assert varBinds[0][1].prettyPrint() == "Shanghai"
        assert isinstance(varBinds[0][1], OctetString)

        snmpDispatcher.transport_dispatcher.close_dispatcher()


@pytest.mark.asyncio
async def test_v1_set_mac_address():
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
                ObjectIdentity("LEXTUDIO-TEST-MIB", "testMacAddress", 0)
            ),  # "1.3.6.1.4.1.60069.9.9.0"
        )
        assert errorIndication is None
        assert errorIndication is None
        assert errorStatus == 0
        assert errorIndex == 0
        assert len(varBinds) == 1
        assert varBinds[0][0].prettyPrint() == "LEXTUDIO-TEST-MIB::testMacAddress.0"
        assert (
            varBinds[0][1].prettyPrint() == "00:11:22:33:44:55"
        )  # IMPORTANT: OCTET STRING Size constraint 6..6

        errorIndication, errorStatus, errorIndex, varBinds = await set_cmd(
            snmpDispatcher,
            CommunityData("public", mpModel=0),
            await UdpTransportTarget.create(("localhost", AGENT_PORT)),
            ObjectType(
                ObjectIdentity("LEXTUDIO-TEST-MIB", "testMacAddress", 0),
                OctetString("00:11:22:33:44:55:66"),  # GitHub issue #141
            ),
        )

        assert errorIndication is None
        assert errorStatus == 3  # bad value
        assert errorIndex == 1
        assert len(varBinds) == 1


@pytest.mark.asyncio
async def test_v1_set_table_creation():
    async with AgentContextManager(enable_table_creation=True):
        snmpDispatcher = SnmpDispatcher()

        # Perform a SNMP walk to get all object counts
        objects = walk_cmd(
            snmpDispatcher,
            CommunityData("public", mpModel=0),
            await UdpTransportTarget.create(("localhost", AGENT_PORT)),
            ObjectType(ObjectIdentity("1.3.6")),
        )

        objects_list = [item async for item in objects]
        assert len(objects_list) > 0

        object_counts = len(objects_list)

        errorIndication, errorStatus, errorIndex, varBinds = await set_cmd(
            snmpDispatcher,
            CommunityData("public", mpModel=0),
            await UdpTransportTarget.create(("localhost", AGENT_PORT)),
            ObjectType(
                ObjectIdentity("1.3.6.6.1.5.2.97.98.99"), OctetString("My value")
            ),
        )

        assert errorIndication is None
        assert errorStatus == 0
        assert len(varBinds) == 1
        assert varBinds[0][0].prettyPrint() == "SNMPv2-SMI::dod.6.1.5.2.97.98.99"
        assert varBinds[0][1].prettyPrint() == "My value"
        assert type(varBinds[0][1]).__name__ == "OctetString"

        errorIndication, errorStatus, errorIndex, varBinds = await set_cmd(
            snmpDispatcher,
            CommunityData("public", mpModel=0),
            await UdpTransportTarget.create(("localhost", AGENT_PORT)),
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
            snmpDispatcher,
            CommunityData("public", mpModel=0),
            await UdpTransportTarget.create(("localhost", AGENT_PORT)),
            ObjectType(ObjectIdentity("1.3.6")),
        )

        objects_list = [item async for item in objects]
        assert len(objects_list) > 0

        assert len(objects_list) == object_counts + 4

        snmpDispatcher.transport_dispatcher.close_dispatcher()
