import pytest
from pysnmp.hlapi.v3arch.asyncio import (
    CommunityData,
    ContextData,
    SnmpEngine,
    set_cmd,
    UdpTransportTarget,
)
from pysnmp.proto.api.v2c import Integer32
from pysnmp.proto.rfc1902 import OctetString
from pysnmp.smi.rfc1902 import ObjectIdentity, ObjectType
from tests.agent_context import AGENT_PORT, AgentContextManager


@pytest.mark.asyncio
async def test_v2_set():
    async with AgentContextManager():
        with SnmpEngine() as snmpEngine:
            errorIndication, errorStatus, errorIndex, varBinds = await set_cmd(
                snmpEngine,
                CommunityData("public"),
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
async def test_v2_set_nonexistent_oid_returns_not_writable():
    """Test that SET to non-existent OID returns notWritable error (issue #230)."""
    async with AgentContextManager():
        with SnmpEngine() as snmpEngine:
            errorIndication, errorStatus, errorIndex, varBinds = await set_cmd(
                snmpEngine,
                CommunityData("public"),
                await UdpTransportTarget.create(("localhost", AGENT_PORT)),
                ContextData(),
                ObjectType(ObjectIdentity("1.3.6.1.4.1.60069.9.99.0"), Integer32(42)),
            )

            assert errorIndication is None
            assert errorStatus.prettyPrint() == "notWritable"
