import asyncio
from datetime import datetime
import pytest

from pysnmp.hlapi.v3arch.asyncio import *
from pysnmp.proto.errind import RequestTimedOut
from pysnmp.proto.rfc1905 import errorStatus as pysnmp_errorStatus

from tests.agent_context import AGENT_PORT, AgentContextManager


@pytest.mark.asyncio
async def test_v1_get():
    async with AgentContextManager():
        with SnmpEngine() as snmpEngine:
            errorIndication, errorStatus, errorIndex, varBinds = await get_cmd(
                snmpEngine,
                CommunityData("public", mpModel=0),
                await UdpTransportTarget.create(("localhost", AGENT_PORT)),
                ContextData(),
                ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)),
            )

            assert errorIndication is None
            assert errorStatus == 0
            assert len(varBinds) == 1
            assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysDescr.0"
            assert varBinds[0][1].prettyPrint().startswith("PySNMP engine version")
            assert isinstance(varBinds[0][1], OctetString)


@pytest.mark.asyncio
async def test_v1_get_ipv6():
    async with AgentContextManager(enable_ipv6=True):
        with SnmpEngine() as snmpEngine:
            errorIndication, errorStatus, errorIndex, varBinds = await get_cmd(
                snmpEngine,
                CommunityData("public", mpModel=0),
                await Udp6TransportTarget.create(("localhost", AGENT_PORT)),
                ContextData(),
                ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)),
            )

            assert errorIndication is None
            assert errorStatus == 0
            assert len(varBinds) == 1
            assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysDescr.0"
            assert varBinds[0][1].prettyPrint().startswith("PySNMP engine version")
            assert isinstance(varBinds[0][1], OctetString)


@pytest.mark.asyncio
async def test_v1_get_timeout_invalid_target():
    with SnmpEngine() as snmpEngine:

        async def run_get():
            errorIndication, errorStatus, errorIndex, varBinds = await get_cmd(
                snmpEngine,
                CommunityData("community_string"),
                await UdpTransportTarget.create(("1.2.3.4", 161), timeout=1, retries=0),
                ContextData(),
                ObjectType(ObjectIdentity("1.3.6.1.4.1.60069.9.1.0")),
            )
            assert isinstance(errorIndication, RequestTimedOut)
            assert errorStatus == 0
            assert errorIndex == 0
            assert len(varBinds) == 0

        start = datetime.now()
        try:
            await asyncio.wait_for(run_get(), timeout=3)
            end = datetime.now()
            elapsed_time = (end - start).total_seconds()
            assert (
                elapsed_time >= 1 and elapsed_time <= 3
            )  # transport timeout is 1 second
        except asyncio.TimeoutError:
            assert False, "Test case timed out"


@pytest.mark.asyncio
async def test_v1_get_slow_object():
    async with AgentContextManager(enable_custom_objects=True):
        with SnmpEngine() as snmpEngine:

            async def run_get():
                errorIndication, errorStatus, errorIndex, varBinds = await get_cmd(
                    snmpEngine,
                    CommunityData("public", mpModel=0),
                    await UdpTransportTarget.create(
                        ("localhost", AGENT_PORT),
                        timeout=1,
                        retries=0,  # TODO: why this timeout did not work?
                    ),
                    ContextData(),
                    ObjectType(ObjectIdentity("1.3.6.1.4.1.60069.9.1.0")),
                )
                assert errorIndication is None
                assert errorStatus == 0
                assert len(varBinds) == 1

            start = datetime.now()
            try:
                await asyncio.wait_for(run_get(), timeout=3)
                end = datetime.now()
                elapsed_time = (end - start).total_seconds()
                assert (
                    elapsed_time >= 2 and elapsed_time <= 3
                )  # 2 seconds is the delay for the object
            except asyncio.TimeoutError:
                assert False, "Test case timed out"


@pytest.mark.asyncio
async def test_v1_get_no_access_object():
    async with AgentContextManager(enable_custom_objects=True):
        with SnmpEngine() as snmpEngine:
            errorIndication, errorStatus, errorIndex, varBinds = await get_cmd(
                snmpEngine,
                CommunityData("public", mpModel=0),
                await UdpTransportTarget.create(
                    ("localhost", AGENT_PORT), timeout=1, retries=0
                ),
                ContextData(),
                ObjectType(ObjectIdentity("1.3.6.1.4.1.60069.9.3")),
            )
            assert errorIndication is None
            assert (
                errorStatus.prettyPrint() == "noSuchName"
            )  # v1 does not have noAccess
