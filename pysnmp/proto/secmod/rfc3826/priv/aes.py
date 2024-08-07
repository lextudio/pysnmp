#
# This file is part of pysnmp software.
#
# Copyright (c) 2005-2020, Ilya Etingof <etingof@gmail.com>
# License: https://www.pysnmp.com/pysnmp/license.html
#
from hashlib import md5, sha1
import random

try:
    from pysnmpcrypto import aes, PysnmpCryptoError

except ImportError:
    PysnmpCryptoError = AttributeError
    aes = None

from pyasn1.type import univ
from pysnmp.proto.secmod.rfc3414.priv import base
from pysnmp.proto.secmod.rfc3414.auth import hmacmd5, hmacsha
from pysnmp.proto.secmod.rfc7860.auth import hmacsha2
from pysnmp.proto.secmod.rfc3414 import localkey
from pysnmp.proto import errind, error

random.seed()


# RFC3826

#


class Aes(base.AbstractEncryptionService):
    serviceID = (1, 3, 6, 1, 6, 3, 10, 1, 2, 4)  # usmAesCfb128Protocol
    keySize = 16
    _localInt = random.randrange(0, 0xFFFFFFFFFFFFFFFF)

    # 3.1.2.1
    def __getEncryptionKey(self, privKey, snmpEngineBoots, snmpEngineTime):
        salt = [
            self._localInt >> 56 & 0xFF,
            self._localInt >> 48 & 0xFF,
            self._localInt >> 40 & 0xFF,
            self._localInt >> 32 & 0xFF,
            self._localInt >> 24 & 0xFF,
            self._localInt >> 16 & 0xFF,
            self._localInt >> 8 & 0xFF,
            self._localInt & 0xFF,
        ]

        if self._localInt == 0xFFFFFFFFFFFFFFFF:
            self._localInt = 0
        else:
            self._localInt += 1

        return self.__getDecryptionKey(
            privKey, snmpEngineBoots, snmpEngineTime, salt
        ) + (univ.OctetString(salt).asOctets(),)

    def __getDecryptionKey(self, privKey, snmpEngineBoots, snmpEngineTime, salt):
        snmpEngineBoots, snmpEngineTime, salt = (
            int(snmpEngineBoots),
            int(snmpEngineTime),
            salt,
        )

        iv = [
            snmpEngineBoots >> 24 & 0xFF,
            snmpEngineBoots >> 16 & 0xFF,
            snmpEngineBoots >> 8 & 0xFF,
            snmpEngineBoots & 0xFF,
            snmpEngineTime >> 24 & 0xFF,
            snmpEngineTime >> 16 & 0xFF,
            snmpEngineTime >> 8 & 0xFF,
            snmpEngineTime & 0xFF,
        ] + salt

        return privKey[: self.keySize].asOctets(), univ.OctetString(iv).asOctets()

    def hashPassphrase(self, authProtocol, privKey):
        if authProtocol == hmacmd5.HmacMd5.serviceID:
            hashAlgo = md5
        elif authProtocol == hmacsha.HmacSha.serviceID:
            hashAlgo = sha1
        elif authProtocol in hmacsha2.HmacSha2.hashAlgorithms:
            hashAlgo = hmacsha2.HmacSha2.hashAlgorithms[authProtocol]
        else:
            raise error.ProtocolError(f"Unknown auth protocol {authProtocol}")
        return localkey.hashPassphrase(privKey, hashAlgo)

    def localizeKey(self, authProtocol, privKey, snmpEngineID):
        if authProtocol == hmacmd5.HmacMd5.serviceID:
            hashAlgo = md5
        elif authProtocol == hmacsha.HmacSha.serviceID:
            hashAlgo = sha1
        elif authProtocol in hmacsha2.HmacSha2.hashAlgorithms:
            hashAlgo = hmacsha2.HmacSha2.hashAlgorithms[authProtocol]
        else:
            raise error.ProtocolError(f"Unknown auth protocol {authProtocol}")
        localPrivKey = localkey.localizeKey(privKey, snmpEngineID, hashAlgo)
        return localPrivKey[: self.keySize]

    # 3.2.4.1
    def encryptData(self, encryptKey, privParameters, dataToEncrypt):
        if aes is None:
            raise error.StatusInformation(errorIndication=errind.encryptionError)

        snmpEngineBoots, snmpEngineTime, salt = privParameters

        # 3.3.1.1
        aesKey, iv, salt = self.__getEncryptionKey(
            encryptKey, snmpEngineBoots, snmpEngineTime
        )

        # 3.3.1.3
        try:
            ciphertext = aes.encrypt(dataToEncrypt, aesKey, iv)

        except PysnmpCryptoError:
            raise error.StatusInformation(
                errorIndication=errind.unsupportedPrivProtocol
            )

        # 3.3.1.4
        return univ.OctetString(ciphertext), univ.OctetString(salt)

    # 3.2.4.2
    def decryptData(self, decryptKey, privParameters, encryptedData):
        if aes is None:
            raise error.StatusInformation(errorIndication=errind.decryptionError)

        snmpEngineBoots, snmpEngineTime, salt = privParameters

        # 3.3.2.1
        if len(salt) != 8:
            raise error.StatusInformation(errorIndication=errind.decryptionError)

        # 3.3.2.3
        aesKey, iv = self.__getDecryptionKey(
            decryptKey, snmpEngineBoots, snmpEngineTime, salt
        )

        try:
            # 3.3.2.4-6
            return aes.decrypt(encryptedData.asOctets(), aesKey, iv)

        except PysnmpCryptoError:
            raise error.StatusInformation(
                errorIndication=errind.unsupportedPrivProtocol
            )
