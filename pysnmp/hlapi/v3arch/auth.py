#
# This file is part of pysnmp software.
#
# Copyright (c) 2005-2019, Ilya Etingof <etingof@gmail.com>
# License: http://snmplabs.com/pysnmp/license.html
#
from pyasn1.compat.octets import null

from pysnmp import error
from pysnmp.entity import config

__all__ = [
    'CommunityData', 'UsmUserData',
    'USM_AUTH_NONE', 'USM_AUTH_HMAC96_MD5',
    'USM_AUTH_HMAC96_SHA', 'USM_AUTH_HMAC128_SHA224',
    'USM_AUTH_HMAC192_SHA256', 'USM_AUTH_HMAC256_SHA384',
    'USM_AUTH_HMAC384_SHA512', 'USM_PRIV_NONE',
    'USM_PRIV_CBC56_DES', 'USM_PRIV_CBC168_3DES',
    'USM_PRIV_CFB128_AES', 'USM_PRIV_CFB192_AES',
    'USM_PRIV_CFB256_AES', 'USM_PRIV_CFB192_AES_BLUMENTHAL',
    'USM_PRIV_CFB256_AES_BLUMENTHAL',
    # backward-compatible constants
    'usm3DESEDEPrivProtocol', 'usmAesCfb128Protocol',
    'usmAesCfb192Protocol', 'usmAesCfb256Protocol',
    'usmAesBlumenthalCfb192Protocol', 'usmAesBlumenthalCfb256Protocol',
    'usmDESPrivProtocol', 'usmHMACMD5AuthProtocol',
    'usmHMACSHAAuthProtocol', 'usmHMAC128SHA224AuthProtocol',
    'usmHMAC192SHA256AuthProtocol', 'usmHMAC256SHA384AuthProtocol',
    'usmHMAC384SHA512AuthProtocol', 'usmNoAuthProtocol',
    'usmNoPrivProtocol'
]


USM_AUTH_NONE = config.USM_AUTH_NONE
"""No Authentication Protocol"""

USM_AUTH_HMAC96_MD5 = config.USM_AUTH_HMAC96_MD5
"""The HMAC-MD5-96 Digest Authentication Protocol (:RFC:`3414#section-6`)"""

USM_AUTH_HMAC96_SHA = config.USM_AUTH_HMAC96_SHA
"""The HMAC-SHA-96 Digest Authentication Protocol AKA SHA-1 (:RFC:`3414#section-7`)"""

USM_AUTH_HMAC128_SHA224 = config.USM_AUTH_HMAC128_SHA224
"""The HMAC-SHA-2 Digest Authentication Protocols (:RFC:`7860`)"""

USM_AUTH_HMAC192_SHA256 = config.USM_AUTH_HMAC192_SHA256
"""The HMAC-SHA-2 Digest Authentication Protocols (:RFC:`7860`)"""

USM_AUTH_HMAC256_SHA384 = config.USM_AUTH_HMAC256_SHA384
"""The HMAC-SHA-2 Digest Authentication Protocols (:RFC:`7860`)"""

USM_AUTH_HMAC384_SHA512 = config.USM_AUTH_HMAC384_SHA512
"""The HMAC-SHA-2 Digest Authentication Protocols (:RFC:`7860`)"""

USM_PRIV_NONE = config.USM_PRIV_NONE
"""No Privacy Protocol"""

USM_PRIV_CBC56_DES = config.USM_PRIV_CBC56_DES
"""The CBC56-DES Symmetric Encryption Protocol (:RFC:`3414#section-8`)"""

USM_PRIV_CBC168_3DES = config.USM_PRIV_CBC168_3DES
"""The 3DES-EDE Symmetric Encryption Protocol (`draft-reeder-snmpv3-usm-3desede-00 <https:://tools.ietf.org/html/draft-reeder-snmpv3-usm-3desede-00#section-5>`_)"""

USM_PRIV_CFB128_AES = config.USM_PRIV_CFB128_AES
"""The CFB128-AES-128 Symmetric Encryption Protocol (:RFC:`3826#section-3`)"""

USM_PRIV_CFB192_AES = config.USM_PRIV_CFB192_AES
"""The CFB128-AES-192 Symmetric Encryption Protocol (`draft-blumenthal-aes-usm-04 <https:://tools.ietf.org/html/draft-blumenthal-aes-usm-04#section-3>`_) with Reeder key localization"""

USM_PRIV_CFB256_AES = config.USM_PRIV_CFB256_AES
"""The CFB128-AES-256 Symmetric Encryption Protocol (`draft-blumenthal-aes-usm-04 <https:://tools.ietf.org/html/draft-blumenthal-aes-usm-04#section-3>`_) with Reeder key localization"""

USM_PRIV_CFB192_AES_BLUMENTHAL = config.USM_PRIV_CFB192_AES_BLUMENTHAL
"""The CFB128-AES-192 Symmetric Encryption Protocol (`draft-blumenthal-aes-usm-04 <https:://tools.ietf.org/html/draft-blumenthal-aes-usm-04#section-3>`_)"""

USM_PRIV_CFB256_AES_BLUMENTHAL = config.USM_PRIV_CFB256_AES_BLUMENTHAL
"""The CFB128-AES-256 Symmetric Encryption Protocol (`draft-blumenthal-aes-usm-04 <https:://tools.ietf.org/html/draft-blumenthal-aes-usm-04#section-3>`_)"""

# Backward-compatible protocol IDs
usmNoAuthProtocol = USM_AUTH_NONE
usmHMACMD5AuthProtocol = USM_AUTH_HMAC96_MD5
usmHMACSHAAuthProtocol = USM_AUTH_HMAC96_SHA
usmHMAC128SHA224AuthProtocol = USM_AUTH_HMAC128_SHA224
usmHMAC192SHA256AuthProtocol = USM_AUTH_HMAC192_SHA256
usmHMAC256SHA384AuthProtocol = USM_AUTH_HMAC256_SHA384
usmHMAC384SHA512AuthProtocol = USM_AUTH_HMAC384_SHA512
usmNoPrivProtocol = USM_PRIV_NONE
usmDESPrivProtocol = USM_PRIV_CBC56_DES
usm3DESEDEPrivProtocol = USM_PRIV_CBC168_3DES
usmAesCfb128Protocol = USM_PRIV_CFB128_AES
usmAesCfb192Protocol = USM_PRIV_CFB192_AES
usmAesCfb256Protocol = USM_PRIV_CFB256_AES
usmAesBlumenthalCfb192Protocol = USM_PRIV_CFB192_AES_BLUMENTHAL
usmAesBlumenthalCfb256Protocol = USM_PRIV_CFB256_AES_BLUMENTHAL


class CommunityData(object):
    """Creates SNMP v1/v2c configuration entry.

    This object can be used by
    :py:class:`~pysnmp.hlapi.asyncore.AsyncCommandGenerator` or
    :py:class:`~pysnmp.hlapi.asyncore.AsyncNotificationOriginator`
    and their derivatives for adding new entries to Local Configuration
    Datastore (LCD) managed by :py:class:`~pysnmp.hlapi.SnmpEngine`
    class instance.

    See :RFC:`2576#section-5.3` for more information on the
    *SNMP-COMMUNITY-MIB::snmpCommunityTable*.

    Parameters
    ----------
    communityIndex: py:class:`str`
        Unique index value of a row in snmpCommunityTable. If it is the
        only positional parameter, it is treated as a *communityName*.
    communityName: py:class:`str`
        SNMP v1/v2c community string.
    mpModel: py:class:`int`
        SNMP version - 0 for SNMPv1 and 1 for SNMPv2c.
    contextEngineId: py:class:`str`
        Indicates the location of the context in which management
        information is accessed when using the community string
        specified by the above communityName.
    contextName: py:class:`str`
        The context in which management information is accessed when
        using the above communityName.
    tag: py:class:`str`
        Arbitrary string that specifies a set of transport endpoints
        from which a command responder application will accept
        management requests with given *communityName* or to which
        notification originator application will send notifications
        when targets are specified by a tag value(s).

        The other way to look at the *tag* feature is that it can make
        specific *communityName* only valid for certain targets.

        The other use-case is when multiple distinct SNMP peers share
        the same *communityName* -- binding each instance of
        *communityName* to transport endpoint lets you distinguish
        SNMP peers from each other (e.g. resolving *communityName* into
        proper *securityName*).

        For more technical information on SNMP configuration tags please
        refer to :RFC:`3413#section-4.1.1` and :RFC:`2576#section-5.3`
        (e.g. the *snmpCommunityTransportTag* object).

        See also: :py:class:`~pysnmp.hlapi.UdpTransportTarget`

    Warnings
    --------
    If the same *communityIndex* value is supplied repeatedly with
    different *communityName* (or other parameters), the later call
    supersedes all previous calls.

    Make sure not to configure duplicate *communityName* values unless
    they have distinct *mpModel* and/or *tag* fields. This will make
    *communityName* based database lookup ambiguous.

    Examples
    --------
    >>> from pysnmp.hlapi import CommunityData
    >>> CommunityData('public')
    CommunityData(communityIndex='s1410706889', communityName=<COMMUNITY>, mpModel=1, contextEngineId=None, contextName='', tag='')
    >>> CommunityData('public', 'public')
    CommunityData(communityIndex='public', communityName=<COMMUNITY>, mpModel=1, contextEngineId=None, contextName='', tag='')
    >>>

    """
    mpModel = 1  # Default is SMIv2
    securityModel = mpModel + 1
    securityLevel = 'noAuthNoPriv'
    contextName = null
    tag = null

    def __init__(self, communityIndex, communityName=None, mpModel=None,
                 contextEngineId=None, contextName=None, tag=None,
                 securityName=None):
        if mpModel is not None:
            self.mpModel = mpModel
            self.securityModel = mpModel + 1
        self.contextEngineId = contextEngineId
        if contextName is not None:
            self.contextName = contextName
        if tag is not None:
            self.tag = tag
        # a single arg is considered as a community name
        if communityName is None:
            communityName, communityIndex = communityIndex, None
        self.communityName = communityName
        # Autogenerate communityIndex if not specified
        if communityIndex is None:
            self.communityIndex = self.securityName = 's%s' % hash(
                (self.communityName, self.mpModel, self.contextEngineId,
                 self.contextName, self.tag)
            )
        else:
            self.communityIndex = communityIndex
            self.securityName = securityName is not None and securityName or communityIndex

    def __hash__(self):
        raise TypeError('%s is not hashable' % self.__class__.__name__)

    def __repr__(self):
        return '%s(communityIndex=%r, communityName=<COMMUNITY>, mpModel=%r, contextEngineId=%r, contextName=%r, tag=%r, securityName=%r)' % (
            self.__class__.__name__,
            self.communityIndex,
            self.mpModel,
            self.contextEngineId,
            self.contextName,
            self.tag,
            self.securityName
        )

    def clone(self, communityIndex=None, communityName=None,
              mpModel=None, contextEngineId=None,
              contextName=None, tag=None, securityName=None):
        # a single arg is considered as a community name
        if communityName is None:
            communityName, communityIndex = communityIndex, None
        return self.__class__(
            communityIndex,
            communityName is None and self.communityName or communityName,
            mpModel is None and self.mpModel or mpModel,
            contextEngineId is None and self.contextEngineId or contextEngineId,
            contextName is None and self.contextName or contextName,
            tag is None and self.tag or tag,
            securityName is None and self.securityName or securityName
        )


class UsmUserData(object):
    """Creates SNMP v3 User Security Model (USM) configuration entry.

    This object can be used by
    :py:class:`~pysnmp.hlapi.asyncore.AsyncCommandGenerator` or
    :py:class:`~pysnmp.hlapi.asyncore.AsyncNotificationOriginator`
    and their derivatives for adding new entries to Local Configuration
    Datastore (LCD) managed by :py:class:`~pysnmp.hlapi.SnmpEngine`
    class instance.

    See :RFC:`3414#section-5` for more information on the
    *SNMP-USER-BASED-SM-MIB::usmUserTable*.

    Parameters
    ----------
    userName: py:class:`str`
        A human readable string representing the name of the SNMP USM user.
    authKey: py:class:`str`
        Initial value of the secret authentication key.  If not set,
        :py:class:`~pysnmp.hlapi.usmNoAuthProtocol`
        is implied.  If set and no *authProtocol* is specified,
        :py:class:`~pysnmp.hlapi.usmHMACMD5AuthProtocol`
        takes effect.
    privKey: py:class:`str`
        Initial value of the secret encryption key.  If not set,
        :py:class:`~pysnmp.hlapi.usmNoPrivProtocol`
        is implied.  If set and no *privProtocol* is specified,
        :py:class:`~pysnmp.hlapi.usmDESPrivProtocol`
        takes effect.
    authProtocol: py:class:`tuple`
        An indication of whether messages sent on behalf of this USM user
        can be authenticated, and if so, the type of authentication protocol
        which is used.

        Supported authentication protocol identifiers are:

        * :py:class:`~pysnmp.hlapi.usmNoAuthProtocol` (default is *authKey* not given)
        * :py:class:`~pysnmp.hlapi.usmHMACMD5AuthProtocol` (default if *authKey* is given)
        * :py:class:`~pysnmp.hlapi.usmHMACSHAAuthProtocol`
        * :py:class:`~pysnmp.hlapi.usmHMAC128SHA224AuthProtocol`
        * :py:class:`~pysnmp.hlapi.usmHMAC192SHA256AuthProtocol`
        * :py:class:`~pysnmp.hlapi.usmHMAC256SHA384AuthProtocol`
        * :py:class:`~pysnmp.hlapi.usmHMAC384SHA512AuthProtocol`
    privProtocol: py:class:`tuple`
        An indication of whether messages sent on behalf of this USM user
        be encrypted, and if so, the type of encryption protocol which is used.

        Supported encryption protocol identifiers are:

        * :py:class:`~pysnmp.hlapi.usmNoPrivProtocol` (default is *authKey* not given)
        * :py:class:`~pysnmp.hlapi.usmDESPrivProtocol` (default if *authKey* is given)
        * :py:class:`~pysnmp.hlapi.usm3DESEDEPrivProtocol`
        * :py:class:`~pysnmp.hlapi.usmAesCfb128Protocol`
        * :py:class:`~pysnmp.hlapi.usmAesCfb192Protocol`
        * :py:class:`~pysnmp.hlapi.usmAesCfb256Protocol`

    Examples
    --------
    >>> from pysnmp.hlapi import UsmUserData
    >>> UsmUserData('testuser', authKey='authenticationkey')
    UsmUserData(userName='testuser', authKey=<AUTHKEY>, privKey=<PRIVKEY>, authProtocol=(1,3,6,1,6,3,10,1,1,2), privProtocol=(1,3,6,1,6,3,10,1,2,1))
    >>> UsmUserData('testuser', authKey='authenticationkey', privKey='encryptionkey')
    UsmUserData(userName='testuser', authKey=<AUTHKEY>, privKey=<PRIVKEY>, authProtocol=(1,3,6,1,6,3,10,1,1,2), privProtocol=(1,3,6,1,6,3,10,1,2,2))
    >>>

    """
    authKey = privKey = None
    authProtocol = config.USM_AUTH_NONE
    privProtocol = config.USM_PRIV_NONE
    securityLevel = 'noAuthNoPriv'
    securityModel = 3
    mpModel = 3
    contextName = null

    def __init__(self, userName,
                 authKey=None, privKey=None,
                 authProtocol=None, privProtocol=None,
                 securityEngineId=None,
                 securityName=None):
        self.userName = userName
        if securityName is None:
            self.securityName = userName
        else:
            self.securityName = securityName

        if authKey is not None:
            self.authKey = authKey
            if authProtocol is None:
                self.authProtocol = config.USM_AUTH_HMAC96_MD5
            else:
                self.authProtocol = authProtocol
            if self.securityLevel != 'authPriv':
                self.securityLevel = 'authNoPriv'

        if privKey is not None:
            self.privKey = privKey
            if self.authProtocol == config.USM_AUTH_NONE:
                raise error.PySnmpError('Privacy implies authenticity')
            self.securityLevel = 'authPriv'
            if privProtocol is None:
                self.privProtocol = config.USM_PRIV_CBC56_DES
            else:
                self.privProtocol = privProtocol

        self.securityEngineId = securityEngineId

    def __hash__(self):
        raise TypeError('%s is not hashable' % self.__class__.__name__)

    def __repr__(self):
        return '%s(userName=%r, authKey=<AUTHKEY>, privKey=<PRIVKEY>, authProtocol=%r, privProtocol=%r, securityEngineId=%r, securityName=%r)' % (
            self.__class__.__name__,
            self.userName,
            self.authProtocol,
            self.privProtocol,
            self.securityEngineId is None and '<DEFAULT>' or self.securityEngineId,
            self.securityName
        )

    def clone(self, userName=None,
              authKey=None, privKey=None,
              authProtocol=None, privProtocol=None,
              securityEngineId=None, securityName=None):
        return self.__class__(
            userName is None and self.userName or userName,
            authKey is None and self.authKey or authKey,
            privKey is None and self.privKey or privKey,
            authProtocol is None and self.authProtocol or authProtocol,
            privProtocol is None and self.privProtocol or privProtocol,
            securityEngineId is None and self.securityEngineId or securityEngineId,
            securityName=securityName is None and self.securityName or securityName
        )