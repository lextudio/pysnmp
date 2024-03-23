#
# This file is part of pysnmp software.
#
# Copyright (c) 2005-2020, Ilya Etingof <etingof@gmail.com>
# License: https://www.pysnmp.com/pysnmp/license.html
#
import random
from hashlib import md5
from hashlib import sha1

try:
    from pysnmpcrypto import aes, PysnmpCryptoError

except ImportError:
    PysnmpCryptoError = AttributeError
    aes = None

from pyasn1.type import univ
from pysnmp.proto.secmod.rfc3414.priv import base
from pysnmp.proto.secmod.rfc3414.auth import hmacmd5
from pysnmp.proto.secmod.rfc3414.auth import hmacsha
from pysnmp.proto.secmod.rfc7860.auth import hmacsha2
from pysnmp.proto.secmod.rfc3414 import localkey
from pysnmp.proto import errind
from pysnmp.proto import error

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
    SERVICE_ID = (1, 3, 6, 1, 6, 3, 10, 1, 2, 4)  # usmAesCfb128Protocol
    KEY_SIZE = 16

    local_int = random.randrange(0, 0xFFFFFFFFFFFFFFFF)

    # 3.1.2.1
    def _getEncryptionKey(self, privKey, snmpEngineBoots, snmpEngineTime):
        salt = [
            self.local_int >> 56 & 0xFF,
            self.local_int >> 48 & 0xFF,
            self.local_int >> 40 & 0xFF,
            self.local_int >> 32 & 0xFF,
            self.local_int >> 24 & 0xFF,
            self.local_int >> 16 & 0xFF,
            self.local_int >> 8 & 0xFF,
            self.local_int & 0xFF,
        ]

        if self.local_int == 0xFFFFFFFFFFFFFFFF:
            self.local_int = 0

        else:
            self.local_int += 1

        key, iv = self._getDecryptionKey(privKey, snmpEngineBoots, snmpEngineTime, salt)

        return key, iv, univ.OctetString(salt).asOctets()

    def _getDecryptionKey(self, privKey, snmpEngineBoots, snmpEngineTime, salt):
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
        ]

        iv += salt

        key = privKey[: self.KEY_SIZE].asOctets()
        iv = univ.OctetString(iv).asOctets()

        return key, iv

    def hashPassphrase(self, authProtocol, privKey):
        if authProtocol == hmacmd5.HmacMd5.SERVICE_ID:
            hashAlgo = md5

        elif authProtocol == hmacsha.HmacSha.SERVICE_ID:
            hashAlgo = sha1

        elif authProtocol in hmacsha2.HmacSha2.HASH_ALGORITHM:
            hashAlgo = hmacsha2.HmacSha2.HASH_ALGORITHM[authProtocol]

        else:
            raise error.ProtocolError(f"Unknown auth protocol {authProtocol}")

        return localkey.hashPassphrase(privKey, hashAlgo)

    def localizeKey(self, authProtocol, privKey, snmpEngineID):
        if authProtocol == hmacmd5.HmacMd5.SERVICE_ID:
            hashAlgo = md5

        elif authProtocol == hmacsha.HmacSha.SERVICE_ID:
            hashAlgo = sha1

        elif authProtocol in hmacsha2.HmacSha2.HASH_ALGORITHM:
            hashAlgo = hmacsha2.HmacSha2.HASH_ALGORITHM[authProtocol]

        else:
            raise error.ProtocolError(f"Unknown auth protocol {authProtocol}")

        localPrivKey = localkey.localizeKey(privKey, snmpEngineID, hashAlgo)

        return localPrivKey[: self.KEY_SIZE]

    # 3.2.4.1
    def encryptData(self, encryptKey, privParameters, dataToEncrypt):
        if aes is None:
            raise error.StatusInformation(errorIndication=errind.encryptionError)

        snmpEngineBoots, snmpEngineTime, salt = privParameters

        # 3.3.1.1
        aesKey, iv, salt = self._getEncryptionKey(
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
        aesKey, iv = self._getDecryptionKey(
            decryptKey, snmpEngineBoots, snmpEngineTime, salt
        )

        try:
            # 3.3.2.4-6
            return aes.decrypt(encryptedData.asOctets(), aesKey, iv)

        except PysnmpCryptoError:
            raise error.StatusInformation(
                errorIndication=errind.unsupportedPrivProtocol
            )
