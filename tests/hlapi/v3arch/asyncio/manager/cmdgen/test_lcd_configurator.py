from unittest import mock

import pytest

from pysnmp.hlapi.v3arch.asyncio import *
from pysnmp.hlapi.v3arch.asyncio.lcd import CommandGeneratorLcdConfigurator


@mock.patch("pysnmp.entity.config.add_v3_user")
@mock.patch("pysnmp.entity.config.delete_v3_user")
@pytest.mark.asyncio
async def test_usm_auth_cache_cleared(delete_v3_user, add_v3_user):
    """
    Ensure auth cache is cleared when auth data is changed.
    """
    snmpEngine = SnmpEngine()
    transportTarget = await UdpTransportTarget.create(("198.51.100.1", 161))

    authDataValues = {
        "userName": "username",
        "authKey": "authkey1",
        "authProtocol": USM_AUTH_HMAC96_MD5,
        "privKey": "privkey1",
        "privProtocol": USM_PRIV_CFB128_AES,
    }

    lcd = CommandGeneratorLcdConfigurator()
    initialAuthData = UsmUserData(**authDataValues)
    lcd.configure(snmpEngine, initialAuthData, transportTarget)
    add_v3_user.assert_called_with(
        snmpEngine,
        initialAuthData.userName,
        initialAuthData.authentication_protocol,
        initialAuthData.authentication_key,
        initialAuthData.privacy_protocol,
        initialAuthData.privacy_key,
        securityEngineId=initialAuthData.securityEngineId,
        securityName=initialAuthData.securityName,
        authKeyType=initialAuthData.authKeyType,
        privKeyType=initialAuthData.privKeyType,
    )

    # Ensure we do not add/delete if nothing changes
    add_v3_user.reset_mock()
    lcd.configure(snmpEngine, initialAuthData, transportTarget)
    add_v3_user.assert_not_called()
    delete_v3_user.assert_not_called()

    changeAuthValues = {
        "authKey": "authKey2",
        "privProtocol": USM_PRIV_CBC56_DES,
        "authProtocol": USM_AUTH_HMAC96_SHA,
        "privKey": "privKey2",
    }

    for field, value in changeAuthValues.items():
        add_v3_user.reset_mock()
        delete_v3_user.reset_mock()

        authDataValues[field] = value
        authData = UsmUserData(**authDataValues)
        lcd.configure(snmpEngine, authData, transportTarget)

        delete_v3_user.assert_called_with(
            snmpEngine,
            authData.userName,
            authData.securityEngineId,
        )

        add_v3_user.assert_called_with(
            snmpEngine,
            authData.userName,
            authData.authentication_protocol,
            authData.authentication_key,
            authData.privacy_protocol,
            authData.privacy_key,
            securityEngineId=authData.securityEngineId,
            securityName=authData.securityName,
            authKeyType=authData.authKeyType,
            privKeyType=authData.privKeyType,
        )
    snmpEngine.close_dispatcher()
