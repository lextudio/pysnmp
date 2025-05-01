import pytest
from pysnmp.hlapi.v1arch.asyncio import *
from pysnmp.proto.rfc1902 import OctetString
from pysnmp.smi.rfc1902 import ObjectIdentity, ObjectType
from tests.agent_context import AGENT_PORT, AgentContextManager


@pytest.mark.asyncio
async def test_v2_set():
    async with AgentContextManager():
        with SnmpDispatcher() as snmpDispatcher:
            errorIndication, errorStatus, errorIndex, varBinds = await set_cmd(
                snmpDispatcher,
                CommunityData("public"),
                await UdpTransportTarget.create(("localhost", AGENT_PORT)),
                ObjectType(ObjectIdentity("SNMPv2-MIB", "sysLocation", 0), "Shanghai"),
            )

            assert errorIndication is None
            assert errorStatus == 0
            assert len(varBinds) == 1
            assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysLocation.0"
            assert varBinds[0][1].prettyPrint() == "Shanghai"
            assert isinstance(varBinds[0][1], OctetString)
