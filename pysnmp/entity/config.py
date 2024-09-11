#
# This file is part of pysnmp software.
#
# Copyright (c) 2005-2020, Ilya Etingof <etingof@gmail.com>
# License: https://www.pysnmp.com/pysnmp/license.html
#
import warnings


from pysnmp import debug, error
from pysnmp.carrier.asyncio.dgram import udp, udp6
from pysnmp.carrier.base import AbstractTransport
from pysnmp.entity.engine import SnmpEngine
from pysnmp.proto import rfc1902, rfc1905
from pysnmp.proto.secmod.eso.priv import aes192, aes256, des3
from pysnmp.proto.secmod.rfc3414.auth import hmacmd5, hmacsha, noauth
from pysnmp.proto.secmod.rfc3414.priv import des, nopriv
from pysnmp.proto.secmod.rfc3826.priv import aes
from pysnmp.proto.secmod.rfc7860.auth import hmacsha2

# Old to new attribute mapping
deprecated_attributes = {
    "snmpUDPDomain": "SNMP_UDP_DOMAIN",
    "snmpUDP6Domain": "SNMP_UDP6_DOMAIN",
    "snmpLocalDomain": "SNMP_LOCAL_DOMAIN",
    "usmHMACMD5AuthProtocol": "USM_AUTH_HMAC96_MD5",
    "usmHMACSHAAuthProtocol": "USM_AUTH_HMAC96_SHA",
    "usmHMAC128SHA224AuthProtocol": "USM_AUTH_HMAC128_SHA224",
    "usmHMAC192SHA256AuthProtocol": "USM_AUTH_HMAC192_SHA256",
    "usmHMAC256SHA384AuthProtocol": "USM_AUTH_HMAC256_SHA384",
    "usmHMAC384SHA512AuthProtocol": "USM_AUTH_HMAC384_SHA512",
    "usmNoAuthProtocol": "USM_AUTH_NONE",
    "usmDESPrivProtocol": "USM_PRIV_CBC56_DES",
    "usm3DESEDEPrivProtocol": "USM_PRIV_CBC168_3DES",
    "usmAesCfb128Protocol": "USM_PRIV_CFB128_AES",
    "usmAesBlumenthalCfb192Protocol": "USM_PRIV_CFB192_AES_BLUMENTHAL",
    "usmAesBlumenthalCfb256Protocol": "USM_PRIV_CFB256_AES_BLUMENTHAL",
    "usmAesCfb192Protocol": "USM_PRIV_CFB192_AES",
    "usmAesCfb256Protocol": "USM_PRIV_CFB256_AES",
    "usmNoPrivProtocol": "USM_PRIV_NONE",
    "usmKeyTypePassphrase": "USM_KEY_TYPE_PASSPHRASE",
    "usmKeyTypeMaster": "USM_KEY_TYPE_MASTER",
    "usmKeyTypeLocalized": "USM_KEY_TYPE_LOCALIZED",
    "authServices": "AUTH_SERVICES",
    "privServices": "PRIV_SERVICES",
}


def __getattr__(attr: str):
    if new_attr := deprecated_attributes.get(attr):
        warnings.warn(
            f"{attr} is deprecated. Please use {new_attr} instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return globals()[new_attr]
    raise AttributeError(f"module '{__name__}' has no attribute '{attr}'")


# A shortcut to popular constants

# Transports
SNMP_UDP_DOMAIN = udp.SNMP_UDP_DOMAIN
SNMP_UDP6_DOMAIN = udp6.SNMP_UDP6_DOMAIN

# Auth protocol
USM_AUTH_HMAC96_MD5 = hmacmd5.HmacMd5.SERVICE_ID
USM_AUTH_HMAC96_SHA = hmacsha.HmacSha.SERVICE_ID
USM_AUTH_HMAC128_SHA224 = hmacsha2.HmacSha2.SHA224_SERVICE_ID
USM_AUTH_HMAC192_SHA256 = hmacsha2.HmacSha2.SHA256_SERVICE_ID
USM_AUTH_HMAC256_SHA384 = hmacsha2.HmacSha2.SAH384_SERVICE_ID
USM_AUTH_HMAC384_SHA512 = hmacsha2.HmacSha2.SHA512_SERVICE_ID

USM_AUTH_NONE = noauth.NoAuth.SERVICE_ID
"""No authentication service"""

# Privacy protocol
USM_PRIV_CBC56_DES = des.Des.SERVICE_ID
USM_PRIV_CBC168_3DES = des3.Des3.SERVICE_ID
USM_PRIV_CFB128_AES = aes.Aes.SERVICE_ID
USM_PRIV_CFB192_AES_BLUMENTHAL = (
    aes192.AesBlumenthal192.SERVICE_ID
)  # semi-standard but not widely used
USM_PRIV_CFB256_AES_BLUMENTHAL = (
    aes256.AesBlumenthal256.SERVICE_ID
)  # semi-standard but not widely used
USM_PRIV_CFB192_AES = aes192.Aes192.SERVICE_ID  # non-standard but used by many vendors
USM_PRIV_CFB256_AES = aes256.Aes256.SERVICE_ID  # non-standard but used by many vendors
USM_PRIV_NONE = nopriv.NoPriv.SERVICE_ID

# USM key types (PYSNMP-USM-MIB::pysnmpUsmKeyType)
USM_KEY_TYPE_PASSPHRASE = 0
USM_KEY_TYPE_MASTER = 1
USM_KEY_TYPE_LOCALIZED = 2

# Auth services
AUTH_SERVICES = {
    hmacmd5.HmacMd5.SERVICE_ID: hmacmd5.HmacMd5(),
    hmacsha.HmacSha.SERVICE_ID: hmacsha.HmacSha(),
    hmacsha2.HmacSha2.SHA224_SERVICE_ID: hmacsha2.HmacSha2(
        hmacsha2.HmacSha2.SHA224_SERVICE_ID
    ),
    hmacsha2.HmacSha2.SHA256_SERVICE_ID: hmacsha2.HmacSha2(
        hmacsha2.HmacSha2.SHA256_SERVICE_ID
    ),
    hmacsha2.HmacSha2.SAH384_SERVICE_ID: hmacsha2.HmacSha2(
        hmacsha2.HmacSha2.SAH384_SERVICE_ID
    ),
    hmacsha2.HmacSha2.SHA512_SERVICE_ID: hmacsha2.HmacSha2(
        hmacsha2.HmacSha2.SHA512_SERVICE_ID
    ),
    noauth.NoAuth.SERVICE_ID: noauth.NoAuth(),
}

# Privacy services
PRIV_SERVICES = {
    des.Des.SERVICE_ID: des.Des(),
    des3.Des3.SERVICE_ID: des3.Des3(),
    aes.Aes.SERVICE_ID: aes.Aes(),
    aes192.AesBlumenthal192.SERVICE_ID: aes192.AesBlumenthal192(),
    aes256.AesBlumenthal256.SERVICE_ID: aes256.AesBlumenthal256(),
    aes192.Aes192.SERVICE_ID: aes192.Aes192(),  # non-standard
    aes256.Aes256.SERVICE_ID: aes256.Aes256(),  # non-standard
    nopriv.NoPriv.SERVICE_ID: nopriv.NoPriv(),
}


def __cookV1SystemInfo(snmpEngine: SnmpEngine, communityIndex):
    mibBuilder = snmpEngine.msgAndPduDsp.mibInstrumController.mibBuilder

    (snmpEngineID,) = mibBuilder.importSymbols("__SNMP-FRAMEWORK-MIB", "snmpEngineID")
    (snmpCommunityEntry,) = mibBuilder.importSymbols(
        "SNMP-COMMUNITY-MIB", "snmpCommunityEntry"
    )
    tblIdx = snmpCommunityEntry.getInstIdFromIndices(communityIndex)
    return snmpCommunityEntry, tblIdx, snmpEngineID


def addV1System(
    snmpEngine: SnmpEngine,
    communityIndex: str,
    communityName: str,
    contextEngineId=None,
    contextName=None,
    transportTag=None,
    securityName=None,
):
    (snmpCommunityEntry, tblIdx, snmpEngineID) = __cookV1SystemInfo(
        snmpEngine, communityIndex
    )

    if contextEngineId is None:
        contextEngineId = snmpEngineID.syntax
    else:
        contextEngineId = snmpEngineID.syntax.clone(contextEngineId)

    if contextName is None:
        contextName = b""

    securityName = securityName is not None and securityName or communityIndex

    snmpEngine.msgAndPduDsp.mibInstrumController.writeVars(
        (snmpCommunityEntry.name + (8,) + tblIdx, "destroy"),
        **dict(snmpEngine=snmpEngine),
    )
    snmpEngine.msgAndPduDsp.mibInstrumController.writeVars(
        (snmpCommunityEntry.name + (1,) + tblIdx, communityIndex),
        (snmpCommunityEntry.name + (2,) + tblIdx, communityName),
        (
            snmpCommunityEntry.name + (3,) + tblIdx,
            securityName is not None and securityName or communityIndex,
        ),
        (snmpCommunityEntry.name + (4,) + tblIdx, contextEngineId),
        (snmpCommunityEntry.name + (5,) + tblIdx, contextName),
        (snmpCommunityEntry.name + (6,) + tblIdx, transportTag),
        (snmpCommunityEntry.name + (7,) + tblIdx, "nonVolatile"),
        (snmpCommunityEntry.name + (8,) + tblIdx, "createAndGo"),
        **dict(snmpEngine=snmpEngine),
    )

    debug.logger & debug.FLAG_SM and debug.logger(
        "addV1System: added new table entry "
        'communityIndex "%s" communityName "%s" securityName "%s" '
        'contextEngineId "%s" contextName "%s" transportTag '
        '"%s"'
        % (
            communityIndex,
            communityName,
            securityName,
            contextEngineId,
            contextName,
            transportTag,
        )
    )


def delV1System(snmpEngine, communityIndex):
    (snmpCommunityEntry, tblIdx, snmpEngineID) = __cookV1SystemInfo(
        snmpEngine, communityIndex
    )
    snmpEngine.msgAndPduDsp.mibInstrumController.writeVars(
        (snmpCommunityEntry.name + (8,) + tblIdx, "destroy"),
        **dict(snmpEngine=snmpEngine),
    )

    debug.logger & debug.FLAG_SM and debug.logger(
        "delV1System: deleted table entry by communityIndex " '"%s"' % (communityIndex,)
    )


def __cookV3UserInfo(snmpEngine, securityName, securityEngineId):
    mibBuilder = snmpEngine.msgAndPduDsp.mibInstrumController.mibBuilder

    (snmpEngineID,) = mibBuilder.importSymbols("__SNMP-FRAMEWORK-MIB", "snmpEngineID")

    if securityEngineId is None:
        securityEngineId = snmpEngineID.syntax
    else:
        securityEngineId = snmpEngineID.syntax.clone(securityEngineId)

    (usmUserEntry,) = mibBuilder.importSymbols("SNMP-USER-BASED-SM-MIB", "usmUserEntry")
    tblIdx1 = usmUserEntry.getInstIdFromIndices(securityEngineId, securityName)

    (pysnmpUsmSecretEntry,) = mibBuilder.importSymbols(
        "PYSNMP-USM-MIB", "pysnmpUsmSecretEntry"
    )
    tblIdx2 = pysnmpUsmSecretEntry.getInstIdFromIndices(securityName)

    return securityEngineId, usmUserEntry, tblIdx1, pysnmpUsmSecretEntry, tblIdx2


def addV3User(
    snmpEngine,
    userName,
    authProtocol=USM_AUTH_NONE,
    authKey=None,
    privProtocol=USM_PRIV_NONE,
    privKey=None,
    securityEngineId=None,
    securityName=None,
    authKeyType=USM_KEY_TYPE_PASSPHRASE,
    privKeyType=USM_KEY_TYPE_PASSPHRASE,
):
    mibBuilder = snmpEngine.msgAndPduDsp.mibInstrumController.mibBuilder

    if securityName is None:
        securityName = userName

    (
        securityEngineId,
        usmUserEntry,
        tblIdx1,
        pysnmpUsmSecretEntry,
        tblIdx2,
    ) = __cookV3UserInfo(snmpEngine, securityName, securityEngineId)

    # Load augmenting table before creating new row in base one
    (pysnmpUsmKeyEntry,) = mibBuilder.importSymbols(
        "PYSNMP-USM-MIB", "pysnmpUsmKeyEntry"
    )

    # Load clone-from (may not be needed)
    (zeroDotZero,) = mibBuilder.importSymbols("SNMPv2-SMI", "zeroDotZero")

    snmpEngine.msgAndPduDsp.mibInstrumController.writeVars(
        (usmUserEntry.name + (13,) + tblIdx1, "destroy"), **dict(snmpEngine=snmpEngine)
    )
    snmpEngine.msgAndPduDsp.mibInstrumController.writeVars(
        (usmUserEntry.name + (2,) + tblIdx1, userName),
        (usmUserEntry.name + (3,) + tblIdx1, securityName),
        (usmUserEntry.name + (4,) + tblIdx1, zeroDotZero.name),
        (usmUserEntry.name + (5,) + tblIdx1, authProtocol),
        (usmUserEntry.name + (8,) + tblIdx1, privProtocol),
        (usmUserEntry.name + (13,) + tblIdx1, "createAndGo"),
        **dict(snmpEngine=snmpEngine),
    )

    if authProtocol not in AUTH_SERVICES:
        raise error.PySnmpError(f"Unknown auth protocol {authProtocol}")

    if privProtocol not in PRIV_SERVICES:
        raise error.PySnmpError(f"Unknown privacy protocol {privProtocol}")

    (pysnmpUsmKeyType,) = mibBuilder.importSymbols(
        "__PYSNMP-USM-MIB", "pysnmpUsmKeyType"
    )

    authKeyType = pysnmpUsmKeyType.syntax.clone(authKeyType)

    # Localize authentication key unless given

    authKey = authKey and rfc1902.OctetString(authKey)

    masterAuthKey = localAuthKey = authKey

    if authKeyType < USM_KEY_TYPE_MASTER:  # pass phrase is given
        masterAuthKey = AUTH_SERVICES[authProtocol].hashPassphrase(authKey or b"")

    if authKeyType < USM_KEY_TYPE_LOCALIZED:  # pass phrase or master key is given
        localAuthKey = AUTH_SERVICES[authProtocol].localizeKey(
            masterAuthKey, securityEngineId
        )

    # Localize privacy key unless given

    privKeyType = pysnmpUsmKeyType.syntax.clone(privKeyType)

    privKey = privKey and rfc1902.OctetString(privKey)

    masterPrivKey = localPrivKey = privKey

    if privKeyType < USM_KEY_TYPE_MASTER:  # pass phrase is given
        masterPrivKey = PRIV_SERVICES[privProtocol].hashPassphrase(
            authProtocol, privKey or b""
        )

    if privKeyType < USM_KEY_TYPE_LOCALIZED:  # pass phrase or master key is given
        localPrivKey = PRIV_SERVICES[privProtocol].localizeKey(
            authProtocol, masterPrivKey, securityEngineId
        )

    # Commit only the keys we have

    snmpEngine.msgAndPduDsp.mibInstrumController.writeVars(
        (pysnmpUsmKeyEntry.name + (1,) + tblIdx1, localAuthKey),
        (pysnmpUsmKeyEntry.name + (2,) + tblIdx1, localPrivKey),
        **dict(snmpEngine=snmpEngine),
    )

    if authKeyType < USM_KEY_TYPE_LOCALIZED:
        snmpEngine.msgAndPduDsp.mibInstrumController.writeVars(
            (pysnmpUsmKeyEntry.name + (3,) + tblIdx1, masterAuthKey),
            **dict(snmpEngine=snmpEngine),
        )

    if privKeyType < USM_KEY_TYPE_LOCALIZED:
        snmpEngine.msgAndPduDsp.mibInstrumController.writeVars(
            (pysnmpUsmKeyEntry.name + (4,) + tblIdx1, masterPrivKey),
            **dict(snmpEngine=snmpEngine),
        )

    snmpEngine.msgAndPduDsp.mibInstrumController.writeVars(
        (pysnmpUsmSecretEntry.name + (4,) + tblIdx2, "destroy"),
        **dict(snmpEngine=snmpEngine),
    )

    # Commit plain-text pass-phrases if we have them

    snmpEngine.msgAndPduDsp.mibInstrumController.writeVars(
        (pysnmpUsmSecretEntry.name + (4,) + tblIdx2, "createAndGo"),
        **dict(snmpEngine=snmpEngine),
    )

    if authKeyType < USM_KEY_TYPE_MASTER:
        snmpEngine.msgAndPduDsp.mibInstrumController.writeVars(
            (pysnmpUsmSecretEntry.name + (1,) + tblIdx2, userName),
            (pysnmpUsmSecretEntry.name + (2,) + tblIdx2, authKey),
            **dict(snmpEngine=snmpEngine),
        )

    if privKeyType < USM_KEY_TYPE_MASTER:
        snmpEngine.msgAndPduDsp.mibInstrumController.writeVars(
            (pysnmpUsmSecretEntry.name + (1,) + tblIdx2, userName),
            (pysnmpUsmSecretEntry.name + (3,) + tblIdx2, privKey),
            **dict(snmpEngine=snmpEngine),
        )

    debug.logger & debug.FLAG_SM and debug.logger(
        "addV3User: added new table entries "
        'userName "%s" securityName "%s" authProtocol %s '
        'privProtocol %s localAuthKey "%s" localPrivKey "%s" '
        'masterAuthKey "%s" masterPrivKey "%s" authKey "%s" '
        'privKey "%s" by index securityName "%s" securityEngineId '
        '"%s"'
        % (
            userName,
            securityName,
            authProtocol,
            privProtocol,
            localAuthKey and localAuthKey.prettyPrint(),
            localPrivKey and localPrivKey.prettyPrint(),
            masterAuthKey and masterAuthKey.prettyPrint(),
            masterPrivKey and masterPrivKey.prettyPrint(),
            authKey and authKey.prettyPrint(),
            privKey and privKey.prettyPrint(),
            securityName,
            securityEngineId.prettyPrint(),
        )
    )


def delV3User(
    snmpEngine,
    userName,
    securityEngineId=None,
):
    (
        securityEngineId,
        usmUserEntry,
        tblIdx1,
        pysnmpUsmSecretEntry,
        tblIdx2,
    ) = __cookV3UserInfo(snmpEngine, userName, securityEngineId)

    snmpEngine.msgAndPduDsp.mibInstrumController.writeVars(
        (usmUserEntry.name + (13,) + tblIdx1, "destroy"), **dict(snmpEngine=snmpEngine)
    )

    snmpEngine.msgAndPduDsp.mibInstrumController.writeVars(
        (pysnmpUsmSecretEntry.name + (4,) + tblIdx2, "destroy"),
        **dict(snmpEngine=snmpEngine),
    )

    debug.logger & debug.FLAG_SM and debug.logger(
        "delV3User: deleted table entries by index "
        'userName "%s" securityEngineId '
        '"%s"' % (userName, securityEngineId.prettyPrint())
    )

    # Drop all derived rows
    varBinds = initialVarBinds = (
        (usmUserEntry.name + (1,), None),  # usmUserEngineID
        (usmUserEntry.name + (2,), None),  # usmUserName
        (usmUserEntry.name + (4,), None),  # usmUserCloneFrom
    )

    while varBinds:
        varBinds = snmpEngine.msgAndPduDsp.mibInstrumController.readNextVars(
            *varBinds, **dict(snmpEngine=snmpEngine)
        )
        if varBinds[0][1].isSameTypeWith(rfc1905.endOfMibView):
            break
        if varBinds[0][0][: len(initialVarBinds[0][0])] != initialVarBinds[0][0]:
            break
        elif varBinds[2][1] == tblIdx1:  # cloned from this entry
            delV3User(snmpEngine, varBinds[1][1], varBinds[0][1])
            varBinds = initialVarBinds


def __cookTargetParamsInfo(snmpEngine, name):
    mibBuilder = snmpEngine.msgAndPduDsp.mibInstrumController.mibBuilder

    (snmpTargetParamsEntry,) = mibBuilder.importSymbols(
        "SNMP-TARGET-MIB", "snmpTargetParamsEntry"
    )
    tblIdx = snmpTargetParamsEntry.getInstIdFromIndices(name)
    return snmpTargetParamsEntry, tblIdx


# mpModel: 0 == SNMPv1, 1 == SNMPv2c, 3 == SNMPv3
def addTargetParams(snmpEngine, name, securityName, securityLevel, mpModel=3):
    if mpModel == 0:
        securityModel = 1
    elif mpModel in (1, 2):
        securityModel = 2
    elif mpModel == 3:
        securityModel = 3
    else:
        raise error.PySnmpError("Unknown MP model %s" % mpModel)

    snmpTargetParamsEntry, tblIdx = __cookTargetParamsInfo(snmpEngine, name)

    snmpEngine.msgAndPduDsp.mibInstrumController.writeVars(
        (snmpTargetParamsEntry.name + (7,) + tblIdx, "destroy"),
        **dict(snmpEngine=snmpEngine),
    )
    snmpEngine.msgAndPduDsp.mibInstrumController.writeVars(
        (snmpTargetParamsEntry.name + (1,) + tblIdx, name),
        (snmpTargetParamsEntry.name + (2,) + tblIdx, mpModel),
        (snmpTargetParamsEntry.name + (3,) + tblIdx, securityModel),
        (snmpTargetParamsEntry.name + (4,) + tblIdx, securityName),
        (snmpTargetParamsEntry.name + (5,) + tblIdx, securityLevel),
        (snmpTargetParamsEntry.name + (7,) + tblIdx, "createAndGo"),
        **dict(snmpEngine=snmpEngine),
    )


def delTargetParams(snmpEngine: SnmpEngine, name: str):
    snmpTargetParamsEntry, tblIdx = __cookTargetParamsInfo(snmpEngine, name)
    snmpEngine.msgAndPduDsp.mibInstrumController.writeVars(
        (snmpTargetParamsEntry.name + (7,) + tblIdx, "destroy"),
        **dict(snmpEngine=snmpEngine),
    )


def __cookTargetAddrInfo(snmpEngine: SnmpEngine, addrName: str):
    mibBuilder = snmpEngine.msgAndPduDsp.mibInstrumController.mibBuilder

    (snmpTargetAddrEntry,) = mibBuilder.importSymbols(
        "SNMP-TARGET-MIB", "snmpTargetAddrEntry"
    )
    (snmpSourceAddrEntry,) = mibBuilder.importSymbols(
        "PYSNMP-SOURCE-MIB", "snmpSourceAddrEntry"
    )
    tblIdx = snmpTargetAddrEntry.getInstIdFromIndices(addrName)
    return snmpTargetAddrEntry, snmpSourceAddrEntry, tblIdx


def addTargetAddr(
    snmpEngine: SnmpEngine,
    addrName: str,
    transportDomain: "tuple[int, ...]",
    transportAddress: "tuple[str, int]",
    params: str,
    timeout: "float | None" = None,
    retryCount: "int | None" = None,
    tagList=b"",
    sourceAddress=None,
):
    mibBuilder = snmpEngine.msgAndPduDsp.mibInstrumController.mibBuilder

    (snmpTargetAddrEntry, snmpSourceAddrEntry, tblIdx) = __cookTargetAddrInfo(
        snmpEngine, addrName
    )

    if transportDomain[: len(SNMP_UDP_DOMAIN)] == SNMP_UDP_DOMAIN:
        (SnmpUDPAddress,) = mibBuilder.importSymbols("SNMPv2-TM", "SnmpUDPAddress")
        transportAddress = SnmpUDPAddress(transportAddress)
        if sourceAddress is None:
            sourceAddress = ("0.0.0.0", 0)
        sourceAddress = SnmpUDPAddress(sourceAddress)
    elif transportDomain[: len(SNMP_UDP6_DOMAIN)] == SNMP_UDP6_DOMAIN:
        (TransportAddressIPv6,) = mibBuilder.importSymbols(
            "TRANSPORT-ADDRESS-MIB", "TransportAddressIPv6"
        )
        transportAddress = TransportAddressIPv6(transportAddress)
        if sourceAddress is None:
            sourceAddress = ("::", 0)
        sourceAddress = TransportAddressIPv6(sourceAddress)

    snmpEngine.msgAndPduDsp.mibInstrumController.writeVars(
        (snmpTargetAddrEntry.name + (9,) + tblIdx, "destroy"),
        **dict(snmpEngine=snmpEngine),
    )
    snmpEngine.msgAndPduDsp.mibInstrumController.writeVars(
        (snmpTargetAddrEntry.name + (1,) + tblIdx, addrName),
        (snmpTargetAddrEntry.name + (2,) + tblIdx, transportDomain),
        (snmpTargetAddrEntry.name + (3,) + tblIdx, transportAddress),
        (snmpTargetAddrEntry.name + (4,) + tblIdx, timeout),
        (snmpTargetAddrEntry.name + (5,) + tblIdx, retryCount),
        (snmpTargetAddrEntry.name + (6,) + tblIdx, tagList),
        (snmpTargetAddrEntry.name + (7,) + tblIdx, params),
        (snmpSourceAddrEntry.name + (1,) + tblIdx, sourceAddress),
        (snmpTargetAddrEntry.name + (9,) + tblIdx, "createAndGo"),
        **dict(snmpEngine=snmpEngine),
    )


def delTargetAddr(snmpEngine: SnmpEngine, addrName: str):
    (snmpTargetAddrEntry, snmpSourceAddrEntry, tblIdx) = __cookTargetAddrInfo(
        snmpEngine, addrName
    )
    snmpEngine.msgAndPduDsp.mibInstrumController.writeVars(
        (snmpTargetAddrEntry.name + (9,) + tblIdx, "destroy"),
        **dict(snmpEngine=snmpEngine),
    )


def addTransport(
    snmpEngine: SnmpEngine,
    transportDomain: "tuple[int, ...]",
    transport: AbstractTransport,
):
    if snmpEngine.transportDispatcher:
        if not transport.isCompatibleWithDispatcher(snmpEngine.transportDispatcher):
            raise error.PySnmpError(
                f"Transport {transport!r} is not compatible with dispatcher {snmpEngine.transportDispatcher!r}"
            )
    else:
        protoTransportDispatcher = transport.PROTO_TRANSPORT_DISPATCHER
        if protoTransportDispatcher is not None:
            snmpEngine.registerTransportDispatcher(protoTransportDispatcher())
            # here we note that we have created transportDispatcher automatically
            snmpEngine.setUserContext(automaticTransportDispatcher=0)

    if snmpEngine.transportDispatcher:
        snmpEngine.transportDispatcher.registerTransport(transportDomain, transport)
        automaticTransportDispatcher = snmpEngine.getUserContext(
            "automaticTransportDispatcher"
        )
        if automaticTransportDispatcher is not None:
            snmpEngine.setUserContext(
                automaticTransportDispatcher=automaticTransportDispatcher + 1
            )


def getTransport(snmpEngine: SnmpEngine, transportDomain: "tuple[int, ...]"):
    if not snmpEngine.transportDispatcher:
        return
    try:
        return snmpEngine.transportDispatcher.getTransport(transportDomain)
    except error.PySnmpError:
        return


def delTransport(snmpEngine: SnmpEngine, transportDomain: "tuple[int, ...]"):
    if not snmpEngine.transportDispatcher:
        return
    transport = getTransport(snmpEngine, transportDomain)
    snmpEngine.transportDispatcher.unregisterTransport(transportDomain)
    # automatically shutdown automatically created transportDispatcher
    automaticTransportDispatcher = snmpEngine.getUserContext(
        "automaticTransportDispatcher"
    )
    if automaticTransportDispatcher is not None:
        automaticTransportDispatcher -= 1
        snmpEngine.setUserContext(
            automaticTransportDispatcher=automaticTransportDispatcher
        )
        if not automaticTransportDispatcher:
            snmpEngine.closeDispatcher()
            snmpEngine.delUserContext(automaticTransportDispatcher)
    return transport


addSocketTransport = addTransport  # noqa: N816
delSocketTransport = delTransport  # noqa: N816


# VACM shortcuts


def __cookVacmContextInfo(snmpEngine, contextName):
    mibBuilder = snmpEngine.msgAndPduDsp.mibInstrumController.mibBuilder
    (vacmContextEntry,) = mibBuilder.importSymbols(
        "SNMP-VIEW-BASED-ACM-MIB", "vacmContextEntry"
    )
    tblIdx = vacmContextEntry.getInstIdFromIndices(contextName)
    return vacmContextEntry, tblIdx


def addContext(snmpEngine, contextName):
    vacmContextEntry, tblIdx = __cookVacmContextInfo(snmpEngine, contextName)

    snmpEngine.msgAndPduDsp.mibInstrumController.writeVars(
        (vacmContextEntry.name + (2,) + tblIdx, "destroy"),
        **dict(snmpEngine=snmpEngine),
    )
    snmpEngine.msgAndPduDsp.mibInstrumController.writeVars(
        (vacmContextEntry.name + (1,) + tblIdx, contextName),
        (vacmContextEntry.name + (2,) + tblIdx, "createAndGo"),
        **dict(snmpEngine=snmpEngine),
    )


def delContext(snmpEngine, contextName):
    vacmContextEntry, tblIdx = __cookVacmContextInfo(snmpEngine, contextName)

    snmpEngine.msgAndPduDsp.mibInstrumController.writeVars(
        (vacmContextEntry.name + (2,) + tblIdx, "destroy"),
        **dict(snmpEngine=snmpEngine),
    )


def __cookVacmGroupInfo(snmpEngine, securityModel, securityName):
    mibBuilder = snmpEngine.msgAndPduDsp.mibInstrumController.mibBuilder

    (vacmSecurityToGroupEntry,) = mibBuilder.importSymbols(
        "SNMP-VIEW-BASED-ACM-MIB", "vacmSecurityToGroupEntry"
    )
    tblIdx = vacmSecurityToGroupEntry.getInstIdFromIndices(securityModel, securityName)
    return vacmSecurityToGroupEntry, tblIdx


def addVacmGroup(snmpEngine, groupName, securityModel, securityName):
    (vacmSecurityToGroupEntry, tblIdx) = __cookVacmGroupInfo(
        snmpEngine, securityModel, securityName
    )
    snmpEngine.msgAndPduDsp.mibInstrumController.writeVars(
        (vacmSecurityToGroupEntry.name + (5,) + tblIdx, "destroy"),
        **dict(snmpEngine=snmpEngine),
    )
    snmpEngine.msgAndPduDsp.mibInstrumController.writeVars(
        (vacmSecurityToGroupEntry.name + (1,) + tblIdx, securityModel),
        (vacmSecurityToGroupEntry.name + (2,) + tblIdx, securityName),
        (vacmSecurityToGroupEntry.name + (3,) + tblIdx, groupName),
        (vacmSecurityToGroupEntry.name + (5,) + tblIdx, "createAndGo"),
        **dict(snmpEngine=snmpEngine),
    )


def delVacmGroup(snmpEngine, securityModel, securityName):
    vacmSecurityToGroupEntry, tblIdx = __cookVacmGroupInfo(
        snmpEngine, securityModel, securityName
    )
    snmpEngine.msgAndPduDsp.mibInstrumController.writeVars(
        (vacmSecurityToGroupEntry.name + (5,) + tblIdx, "destroy"),
        **dict(snmpEngine=snmpEngine),
    )


def __cookVacmAccessInfo(
    snmpEngine, groupName, contextName, securityModel, securityLevel
):
    mibBuilder = snmpEngine.msgAndPduDsp.mibInstrumController.mibBuilder

    (vacmAccessEntry,) = mibBuilder.importSymbols(
        "SNMP-VIEW-BASED-ACM-MIB", "vacmAccessEntry"
    )
    tblIdx = vacmAccessEntry.getInstIdFromIndices(
        groupName, contextName, securityModel, securityLevel
    )
    return vacmAccessEntry, tblIdx


def addVacmAccess(
    snmpEngine,
    groupName,
    contextPrefix,
    securityModel,
    securityLevel,
    contextMatch,
    readView,
    writeView,
    notifyView,
):
    vacmAccessEntry, tblIdx = __cookVacmAccessInfo(
        snmpEngine, groupName, contextPrefix, securityModel, securityLevel
    )

    snmpEngine.msgAndPduDsp.mibInstrumController.writeVars(
        (vacmAccessEntry.name + (9,) + tblIdx, "destroy"), **dict(snmpEngine=snmpEngine)
    )
    snmpEngine.msgAndPduDsp.mibInstrumController.writeVars(
        (vacmAccessEntry.name + (1,) + tblIdx, contextPrefix),
        (vacmAccessEntry.name + (2,) + tblIdx, securityModel),
        (vacmAccessEntry.name + (3,) + tblIdx, securityLevel),
        (vacmAccessEntry.name + (4,) + tblIdx, contextMatch),
        (vacmAccessEntry.name + (5,) + tblIdx, readView),
        (vacmAccessEntry.name + (6,) + tblIdx, writeView),
        (vacmAccessEntry.name + (7,) + tblIdx, notifyView),
        (vacmAccessEntry.name + (9,) + tblIdx, "createAndGo"),
        **dict(snmpEngine=snmpEngine),
    )


def delVacmAccess(snmpEngine, groupName, contextPrefix, securityModel, securityLevel):
    vacmAccessEntry, tblIdx = __cookVacmAccessInfo(
        snmpEngine, groupName, contextPrefix, securityModel, securityLevel
    )

    snmpEngine.msgAndPduDsp.mibInstrumController.writeVars(
        (vacmAccessEntry.name + (9,) + tblIdx, "destroy"), **dict(snmpEngine=snmpEngine)
    )


def __cookVacmViewInfo(snmpEngine, viewName, subTree):
    mibBuilder = snmpEngine.msgAndPduDsp.mibInstrumController.mibBuilder

    (vacmViewTreeFamilyEntry,) = mibBuilder.importSymbols(
        "SNMP-VIEW-BASED-ACM-MIB", "vacmViewTreeFamilyEntry"
    )
    tblIdx = vacmViewTreeFamilyEntry.getInstIdFromIndices(viewName, subTree)
    return vacmViewTreeFamilyEntry, tblIdx


def addVacmView(snmpEngine, viewName, viewType, subTree, subTreeMask):
    vacmViewTreeFamilyEntry, tblIdx = __cookVacmViewInfo(snmpEngine, viewName, subTree)

    # Allow bitmask specification in form of an OID
    if rfc1902.OctetString(".").asOctets() in rfc1902.OctetString(subTreeMask):
        subTreeMask = rfc1902.ObjectIdentifier(subTreeMask)

    if isinstance(subTreeMask, rfc1902.ObjectIdentifier):
        subTreeMask = tuple(subTreeMask)
        if len(subTreeMask) < len(subTree):
            subTreeMask += (1,) * (len(subTree) - len(subTreeMask))

        subTreeMask = rfc1902.OctetString.fromBinaryString(
            "".join(str(x) for x in subTreeMask)
        )

    snmpEngine.msgAndPduDsp.mibInstrumController.writeVars(
        (vacmViewTreeFamilyEntry.name + (6,) + tblIdx, "destroy"),
        **dict(snmpEngine=snmpEngine),
    )
    snmpEngine.msgAndPduDsp.mibInstrumController.writeVars(
        (vacmViewTreeFamilyEntry.name + (1,) + tblIdx, viewName),
        (vacmViewTreeFamilyEntry.name + (2,) + tblIdx, subTree),
        (vacmViewTreeFamilyEntry.name + (3,) + tblIdx, subTreeMask),
        (vacmViewTreeFamilyEntry.name + (4,) + tblIdx, viewType),
        (vacmViewTreeFamilyEntry.name + (6,) + tblIdx, "createAndGo"),
        **dict(snmpEngine=snmpEngine),
    )


def delVacmView(snmpEngine, viewName, subTree):
    vacmViewTreeFamilyEntry, tblIdx = __cookVacmViewInfo(snmpEngine, viewName, subTree)
    snmpEngine.msgAndPduDsp.mibInstrumController.writeVars(
        (vacmViewTreeFamilyEntry.name + (6,) + tblIdx, "destroy"),
        **dict(snmpEngine=snmpEngine),
    )


# VACM simplicity wrappers


def __cookVacmUserInfo(snmpEngine, securityModel, securityName, securityLevel):
    mibBuilder = snmpEngine.msgAndPduDsp.mibInstrumController.mibBuilder

    groupName = "v-%s-%d" % (hash(securityName), securityModel)
    (SnmpSecurityLevel,) = mibBuilder.importSymbols(
        "SNMP-FRAMEWORK-MIB", "SnmpSecurityLevel"
    )
    securityLevel = SnmpSecurityLevel(securityLevel)
    return (groupName, securityLevel, "r" + groupName, "w" + groupName, "n" + groupName)


def addVacmUser(
    snmpEngine: SnmpEngine,
    securityModel: int,
    securityName: str,
    securityLevel: str,
    readSubTree=(),
    writeSubTree=(),
    notifySubTree=(),
    contextName=b"",
):
    (groupName, securityLevel, readView, writeView, notifyView) = __cookVacmUserInfo(
        snmpEngine, securityModel, securityName, securityLevel
    )
    addContext(snmpEngine, contextName)
    addVacmGroup(snmpEngine, groupName, securityModel, securityName)
    addVacmAccess(
        snmpEngine,
        groupName,
        contextName,
        securityModel,
        securityLevel,
        "exact",
        readView,
        writeView,
        notifyView,
    )
    if readSubTree:
        addVacmView(snmpEngine, readView, "included", readSubTree, b"")
    if writeSubTree:
        addVacmView(snmpEngine, writeView, "included", writeSubTree, b"")
    if notifySubTree:
        addVacmView(snmpEngine, notifyView, "included", notifySubTree, b"")


def delVacmUser(
    snmpEngine,
    securityModel,
    securityName,
    securityLevel,
    readSubTree=(),
    writeSubTree=(),
    notifySubTree=(),
    contextName=b"",
):
    (groupName, securityLevel, readView, writeView, notifyView) = __cookVacmUserInfo(
        snmpEngine, securityModel, securityName, securityLevel
    )
    delContext(snmpEngine, contextName)
    delVacmGroup(snmpEngine, securityModel, securityName)
    delVacmAccess(snmpEngine, groupName, contextName, securityModel, securityLevel)
    if readSubTree:
        delVacmView(snmpEngine, readView, readSubTree)
    if writeSubTree:
        delVacmView(snmpEngine, writeView, writeSubTree)
    if notifySubTree:
        delVacmView(snmpEngine, notifyView, notifySubTree)


# Notification target setup


def __cookNotificationTargetInfo(
    snmpEngine, notificationName, paramsName, filterSubtree=None
):
    mibBuilder = snmpEngine.msgAndPduDsp.mibInstrumController.mibBuilder

    (snmpNotifyEntry,) = mibBuilder.importSymbols(
        "SNMP-NOTIFICATION-MIB", "snmpNotifyEntry"
    )
    tblIdx1 = snmpNotifyEntry.getInstIdFromIndices(notificationName)

    (snmpNotifyFilterProfileEntry,) = mibBuilder.importSymbols(
        "SNMP-NOTIFICATION-MIB", "snmpNotifyFilterProfileEntry"
    )
    tblIdx2 = snmpNotifyFilterProfileEntry.getInstIdFromIndices(paramsName)

    profileName = "%s-filter" % hash(notificationName)

    if filterSubtree:
        (snmpNotifyFilterEntry,) = mibBuilder.importSymbols(
            "SNMP-NOTIFICATION-MIB", "snmpNotifyFilterEntry"
        )
        tblIdx3 = snmpNotifyFilterEntry.getInstIdFromIndices(profileName, filterSubtree)
    else:
        snmpNotifyFilterEntry = tblIdx3 = None

    return (
        snmpNotifyEntry,
        tblIdx1,
        snmpNotifyFilterProfileEntry,
        tblIdx2,
        profileName,
        snmpNotifyFilterEntry,
        tblIdx3,
    )


def addNotificationTarget(
    snmpEngine,
    notificationName,
    paramsName,
    transportTag,
    notifyType=None,
    filterSubtree=None,
    filterMask=None,
    filterType=None,
):
    (
        snmpNotifyEntry,
        tblIdx1,
        snmpNotifyFilterProfileEntry,
        tblIdx2,
        profileName,
        snmpNotifyFilterEntry,
        tblIdx3,
    ) = __cookNotificationTargetInfo(
        snmpEngine, notificationName, paramsName, filterSubtree
    )

    snmpEngine.msgAndPduDsp.mibInstrumController.writeVars(
        (snmpNotifyEntry.name + (5,) + tblIdx1, "destroy"),
        **dict(snmpEngine=snmpEngine),
    )
    snmpEngine.msgAndPduDsp.mibInstrumController.writeVars(
        (snmpNotifyEntry.name + (2,) + tblIdx1, transportTag),
        (snmpNotifyEntry.name + (3,) + tblIdx1, notifyType),
        (snmpNotifyEntry.name + (5,) + tblIdx1, "createAndGo"),
        **dict(snmpEngine=snmpEngine),
    )

    snmpEngine.msgAndPduDsp.mibInstrumController.writeVars(
        (snmpNotifyFilterProfileEntry.name + (3,) + tblIdx2, "destroy"),
        **dict(snmpEngine=snmpEngine),
    )
    snmpEngine.msgAndPduDsp.mibInstrumController.writeVars(
        (snmpNotifyFilterProfileEntry.name + (1,) + tblIdx2, profileName),
        (snmpNotifyFilterProfileEntry.name + (3,) + tblIdx2, "createAndGo"),
        **dict(snmpEngine=snmpEngine),
    )

    if not snmpNotifyFilterEntry:
        return

    snmpEngine.msgAndPduDsp.mibInstrumController.writeVars(
        (snmpNotifyFilterEntry.name + (5,) + tblIdx3, "destroy"),
        **dict(snmpEngine=snmpEngine),
    )
    snmpEngine.msgAndPduDsp.mibInstrumController.writeVars(
        (snmpNotifyFilterEntry.name + (1,) + tblIdx3, filterSubtree),
        (snmpNotifyFilterEntry.name + (2,) + tblIdx3, filterMask),
        (snmpNotifyFilterEntry.name + (3,) + tblIdx3, filterType),
        (snmpNotifyFilterEntry.name + (5,) + tblIdx3, "createAndGo"),
        **dict(snmpEngine=snmpEngine),
    )


def delNotificationTarget(snmpEngine, notificationName, paramsName, filterSubtree=None):
    (
        snmpNotifyEntry,
        tblIdx1,
        snmpNotifyFilterProfileEntry,
        tblIdx2,
        profileName,
        snmpNotifyFilterEntry,
        tblIdx3,
    ) = __cookNotificationTargetInfo(
        snmpEngine, notificationName, paramsName, filterSubtree
    )

    snmpEngine.msgAndPduDsp.mibInstrumController.writeVars(
        (snmpNotifyEntry.name + (5,) + tblIdx1, "destroy"),
        **dict(snmpEngine=snmpEngine),
    )

    snmpEngine.msgAndPduDsp.mibInstrumController.writeVars(
        (snmpNotifyFilterProfileEntry.name + (3,) + tblIdx2, "destroy"),
        **dict(snmpEngine=snmpEngine),
    )

    if not snmpNotifyFilterEntry:
        return

    snmpEngine.msgAndPduDsp.mibInstrumController.writeVars(
        (snmpNotifyFilterEntry.name + (5,) + tblIdx3, "destroy"),
        **dict(snmpEngine=snmpEngine),
    )


# rfc3415: A.1
def setInitialVacmParameters(snmpEngine):
    # rfc3415: A.1.1 --> initial-semi-security-configuration

    # rfc3415: A.1.2
    addContext(snmpEngine, "")

    # rfc3415: A.1.3
    addVacmGroup(snmpEngine, "initial", 3, "initial")

    # rfc3415: A.1.4
    addVacmAccess(
        snmpEngine,
        "initial",
        "",
        3,
        "noAuthNoPriv",
        "exact",
        "restricted",
        None,
        "restricted",
    )
    addVacmAccess(
        snmpEngine,
        "initial",
        "",
        3,
        "authNoPriv",
        "exact",
        "internet",
        "internet",
        "internet",
    )
    addVacmAccess(
        snmpEngine,
        "initial",
        "",
        3,
        "authPriv",
        "exact",
        "internet",
        "internet",
        "internet",
    )

    # rfc3415: A.1.5 (semi-secure)
    addVacmView(snmpEngine, "internet", "included", (1, 3, 6, 1), "")
    addVacmView(snmpEngine, "restricted", "included", (1, 3, 6, 1, 2, 1, 1), "")
    addVacmView(snmpEngine, "restricted", "included", (1, 3, 6, 1, 2, 1, 11), "")
    addVacmView(snmpEngine, "restricted", "included", (1, 3, 6, 1, 6, 3, 10, 2, 1), "")
    addVacmView(snmpEngine, "restricted", "included", (1, 3, 6, 1, 6, 3, 11, 2, 1), "")
    addVacmView(snmpEngine, "restricted", "included", (1, 3, 6, 1, 6, 3, 15, 1, 1), "")
