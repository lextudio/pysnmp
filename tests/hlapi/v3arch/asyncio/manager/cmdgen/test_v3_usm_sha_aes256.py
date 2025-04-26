import pytest
from pysnmp.hlapi.v3arch.asyncio import *
from pysnmp.proto.errind import DecryptionError, UnknownUserName, WrongDigest
from tests.agent_context import AGENT_PORT, AgentContextManager


@pytest.mark.asyncio
async def test_usm_sha_aes256():
    async with AgentContextManager():
        with SnmpEngine() as snmpEngine:
            authData = UsmUserData(
                "usr-sha-aes256",
                "authkey1",
                "privkey1",
                authProtocol=USM_AUTH_HMAC96_SHA,
                privProtocol=USM_PRIV_CFB256_AES,
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
async def test_usm_sha_aes256_wrong_auth():
    async with AgentContextManager():
        with SnmpEngine() as snmpEngine:
            authData = UsmUserData(
                "usr-sha-aes",
                "authkey1",
                "privkey1",
                authProtocol=USM_AUTH_HMAC96_MD5,  # wrongly use usmHMACMD5AuthProtocol
                privProtocol=USM_PRIV_CFB256_AES,
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
async def test_usm_sha_aes256_wrong_user():
    async with AgentContextManager():
        with SnmpEngine() as snmpEngine:
            authData = UsmUserData(
                "usr-sha-aes-not-exist",
                "authkey1",
                "privkey1",
                authProtocol=USM_AUTH_HMAC96_SHA,
                privProtocol=USM_PRIV_CFB256_AES,
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
