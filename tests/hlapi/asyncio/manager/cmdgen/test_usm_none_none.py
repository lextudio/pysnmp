import pytest
from pysnmp.hlapi.v3arch.asyncio import *
from pysnmp.proto.errind import UnknownUserName
from tests.agent_context import AGENT_PORT, AgentContextManager


@pytest.mark.asyncio
async def test_usm_no_auth_no_priv():
    async with AgentContextManager():
        snmpEngine = SnmpEngine()
        authData = UsmUserData("usr-none-none")
        errorIndication, errorStatus, errorIndex, varBinds = await (await getCmd(
            snmpEngine,
            authData,
            UdpTransportTarget(("localhost", AGENT_PORT), retries=0),
            ContextData(),
            ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)),
        ))

        assert errorIndication is None
        assert errorStatus == 0
        assert len(varBinds) == 1
        assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysDescr.0"
        assert varBinds[0][1].prettyPrint().startswith("PySNMP engine version")
        isinstance(varBinds[0][1], OctetString)


@pytest.mark.asyncio
async def test_usm_no_auth_no_priv_wrong_user():
    async with AgentContextManager():
        snmpEngine = SnmpEngine()
        authData = UsmUserData("usr-none-none-not-exist")
        errorIndication, errorStatus, errorIndex, varBinds = await (await getCmd(
            snmpEngine,
            authData,
            UdpTransportTarget(("localhost", AGENT_PORT), retries=0),
            ContextData(),
            ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)),
        ))

        assert isinstance(errorIndication, UnknownUserName)
        assert str(errorIndication) == "Unknown USM user"
        snmpEngine.transportDispatcher.closeDispatcher()
