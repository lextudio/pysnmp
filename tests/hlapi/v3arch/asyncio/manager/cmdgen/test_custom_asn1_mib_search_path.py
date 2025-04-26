import pytest
from pysnmp.hlapi.v3arch.asyncio import *
from tests.agent_context import AGENT_PORT, AgentContextManager


@pytest.mark.asyncio
async def test_custom_asn1_mib_search_path():
    async with AgentContextManager():
        with SnmpEngine() as snmpEngine:
            errorIndication, errorStatus, errorIndex, varBinds = await get_cmd(
                snmpEngine,
                CommunityData("public"),
                await UdpTransportTarget.create(("localhost", AGENT_PORT)),
                ContextData(),
                ObjectType(
                    ObjectIdentity("IF-MIB", "ifInOctets", 1).add_asn1_mib_source(
                        "file:///usr/share/snmp", "https://mibs.pysnmp.com/asn1/@mib@"
                    )
                ),
            )

            assert errorIndication is None
            assert errorStatus == 0
            assert len(varBinds) == 1
            assert varBinds[0][0].prettyPrint() == "IF-MIB::ifInOctets.1"
