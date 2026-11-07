import pytest
from pyasn1.codec.ber import decoder
from pysnmp.hlapi.v3arch.asyncio import *
from pysnmp.proto.mpmod.rfc3412 import SNMPv3Message
from pysnmp.proto.errind import UnknownUserName, WrongDigest
from tests.agent_context import AGENT_PORT, AgentContextManager


@pytest.mark.asyncio
async def test_usm_sha_none():
    async with AgentContextManager():
        with SnmpEngine() as snmpEngine:
            authData = UsmUserData(
                "usr-sha-none",
                "authkey1",
                authProtocol=USM_AUTH_HMAC96_SHA,
            )
            errorIndication, errorStatus, errorIndex, varBinds = await get_cmd(
                snmpEngine,
                authData,
                await UdpTransportTarget.create(("localhost", AGENT_PORT), retries=0),
                ContextData(),
                ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)),
            )

            assert errorIndication is None
            assert errorStatus == 0
            assert len(varBinds) == 1
            assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysDescr.0"
            isinstance(varBinds[0][1], OctetString)


@pytest.mark.asyncio
async def test_usm_sha_none_wrong_auth():
    async with AgentContextManager():
        with SnmpEngine() as snmpEngine:
            authData = UsmUserData(
                "usr-sha-none",
                "authkey1",
                authProtocol=USM_AUTH_HMAC96_MD5,  # wrongly use usmHMACMD5AuthProtocol
            )
            errorIndication, errorStatus, errorIndex, varBinds = await get_cmd(
                snmpEngine,
                authData,
                await UdpTransportTarget.create(("localhost", AGENT_PORT), retries=0),
                ContextData(),
                ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)),
            )

            assert isinstance(errorIndication, WrongDigest)
            assert str(errorIndication) == "Wrong SNMP PDU digest"


@pytest.mark.asyncio
async def test_usm_sha_none_wrong_user():
    async with AgentContextManager():
        with SnmpEngine() as snmpEngine:
            authData = UsmUserData(
                "usr-sha-none-not-exist",
                "authkey1",
                authProtocol=USM_AUTH_HMAC96_SHA,
            )
            errorIndication, errorStatus, errorIndex, varBinds = await get_cmd(
                snmpEngine,
                authData,
                await UdpTransportTarget.create(("localhost", AGENT_PORT), retries=0),
                ContextData(),
                ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)),
            )

            assert isinstance(errorIndication, UnknownUserName)
            assert str(errorIndication) == "Unknown USM user"


@pytest.mark.asyncio
async def test_usm_sha_none_wrong_user_report_not_reportable(monkeypatch):
    async with AgentContextManager() as agent:
        sent = []
        send_message = agent.transport_dispatcher.send_message

        def capture(message, *args):
            sent.append(decoder.decode(message, asn1Spec=SNMPv3Message())[0])
            send_message(message, *args)

        monkeypatch.setattr(agent.transport_dispatcher, "send_message", capture)

        with SnmpEngine() as snmpEngine:
            authData = UsmUserData(
                "usr-sha-none-not-exist",
                "authkey1",
                authProtocol=USM_AUTH_HMAC96_SHA,
            )
            errorIndication, errorStatus, errorIndex, varBinds = await get_cmd(
                snmpEngine,
                authData,
                await UdpTransportTarget.create(("localhost", AGENT_PORT), retries=0),
                ContextData(),
                ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)),
            )

            assert isinstance(errorIndication, UnknownUserName)
            # both Reports: noAuthNoPriv, not reportable (#207)
            flags = [bytes(m["msgGlobalData"]["msgFlags"]) for m in sent]
            assert flags == [b"\x00", b"\x00"]
