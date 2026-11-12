import warnings

from cryptography.utils import CryptographyDeprecationWarning
from pyasn1.type import univ

# Initialize the USM package before importing its AES privacy service.
from pysnmp.proto.secmod.rfc3414 import service  # noqa: F401
from pysnmp.proto.secmod.rfc3826.priv.aes import Aes


def test_aes_cfb_encrypt_decrypt_emits_no_cryptography_deprecation_warning():
    aes_service = Aes()
    key = univ.OctetString(b"0123456789abcdef")
    plaintext = b"SNMPv3 AES-CFB128 test payload"

    with warnings.catch_warnings():
        warnings.simplefilter("error", CryptographyDeprecationWarning)
        ciphertext, salt = aes_service.encrypt_data(key, (1, 2, None), plaintext)
        decrypted = aes_service.decrypt_data(key, (1, 2, salt), ciphertext)

    assert decrypted == plaintext
