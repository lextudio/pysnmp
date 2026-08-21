#
# This file is part of pysnmp software.
#
# Copyright (c) 2024, LeXtudio Inc. <support@lextudio.com>
# License: https://www.pysnmp.com/pysnmp/license.html
#
# RFC 2786 — Diffie-Hellman USM Key Management Extensions
#
"""DH key exchange primitives for RFC 2786 USM key management.

Oakley Group 2 (RFC 2409) is used as the default DH group:
  - 1024-bit prime p
  - generator g = 2
  - private value length = 1024 bits
"""

import os
from dataclasses import dataclass

from pyasn1.codec.ber import decoder as ber_decoder, encoder as ber_encoder
from pyasn1.type import namedtype, univ


@dataclass(frozen=True)
class DHParameters:
    """Internal representation of DH parameters.

    This avoids depending on ``cryptography`` for parameter representation.
    The ``cryptography`` library is only imported when actual cryptographic
    operations (key generation) are performed.
    """

    p: int
    g: int

    def bit_length(self) -> int:
        """Return the bit length of the prime *p*."""
        return self.p.bit_length()


__all__ = [
    "OAKLEY_GROUP2_PRIME",
    "OAKLEY_GROUP2_GENERATOR",
    "DHParameters",
    "get_default_parameters",
    "decode_parameters",
    "encode_parameters",
    "generate_key_pair",
    "compute_shared_secret",
    "derive_key",
    "int_to_bytes",
    "bytes_to_int",
]

# ---------------------------------------------------------------------------
# Oakley Group 2 (RFC 2409 §6.2, RFC 2786 default)
# ---------------------------------------------------------------------------

OAKLEY_GROUP2_PRIME = int(
    "FFFFFFFF"
    "FFFFFFFF"
    "C90FDAA2"
    "2168C234"
    "C4C6628B"
    "80DC1CD1"
    "29024E08"
    "8A67CC74"
    "020BBEA6"
    "3B139B22"
    "514A0879"
    "8E3404DD"
    "EF9519B3"
    "CD3A431B"
    "302B0A6D"
    "F25F1437"
    "4FE1356D"
    "6D51C245"
    "E485B576"
    "625E7EC6"
    "F44C42E9"
    "A637ED6B"
    "0BFF5CB6"
    "F406B7ED"
    "EE386BFB"
    "5A899FA5"
    "AE9F2411"
    "7C4B1FE6"
    "49286651"
    "ECE65381"
    "FFFFFFFF"
    "FFFFFFFF",
    16,
)
OAKLEY_GROUP2_GENERATOR = 2
OAKLEY_GROUP2_PRIVATE_BITS = 1024


# ---------------------------------------------------------------------------
# PKCS#3 DHParameter ASN.1 structure
# ---------------------------------------------------------------------------


class _DHParameter(univ.Sequence):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType("prime", univ.Integer()),
        namedtype.NamedType("base", univ.Integer()),
        namedtype.OptionalNamedType("privateValueLength", univ.Integer()),
    )


# ---------------------------------------------------------------------------
# Parameter helpers
# ---------------------------------------------------------------------------


def get_default_parameters() -> DHParameters:
    """Return DHParameters for Oakley Group 2."""
    return DHParameters(OAKLEY_GROUP2_PRIME, OAKLEY_GROUP2_GENERATOR)


def decode_parameters(der_bytes: bytes) -> DHParameters:
    """Decode a PKCS#3 DER-encoded DHParameter SEQUENCE into DHParameters."""
    asn1, _ = ber_decoder.decode(der_bytes, asn1Spec=_DHParameter())
    p = int(asn1["prime"])
    g = int(asn1["base"])
    return DHParameters(p, g)


def encode_parameters(params: DHParameters, private_value_length: int = 0) -> bytes:
    """Encode DHParameters as a PKCS#3 DER DHParameter SEQUENCE."""
    asn1 = _DHParameter()
    asn1["prime"] = params.p
    asn1["base"] = params.g
    if private_value_length:
        asn1["privateValueLength"] = private_value_length
    return ber_encoder.encode(asn1)


# ---------------------------------------------------------------------------
# Byte / integer conversion
# ---------------------------------------------------------------------------


def int_to_bytes(n: int, length: int | None = None) -> bytes:
    """Convert a non-negative integer to big-endian bytes.

    If *length* is given the result is zero-padded (or truncated) to that many
    bytes.
    """
    if n == 0:
        b = b"\x00"
    else:
        byte_length = (n.bit_length() + 7) // 8
        b = n.to_bytes(byte_length, "big")
    if length is not None:
        if len(b) < length:
            b = b.rjust(length, b"\x00")
        elif len(b) > length:
            b = b[-length:]
    return b


def bytes_to_int(b: bytes) -> int:
    """Convert big-endian bytes to a non-negative integer."""
    return int.from_bytes(b, "big")


# ---------------------------------------------------------------------------
# Key generation and exchange
# ---------------------------------------------------------------------------


def generate_key_pair(
    params: DHParameters | None = None,
) -> tuple[int, int]:
    """Generate a DH key pair using *params* (defaults to Oakley Group 2).

    Returns *(private_int, public_int)*.

    Raises ImportError if ``cryptography`` is not installed.
    """
    try:
        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives.asymmetric.dh import (
            DHParameterNumbers,
        )
    except ImportError as exc:
        raise ImportError(
            "DH key generation requires the 'cryptography' package. "
            "Install it with: pip install pysnmp[crypto]"
        ) from exc

    if params is None:
        params = get_default_parameters()
    crypto_params = DHParameterNumbers(params.p, params.g).parameters(default_backend())
    private_key = crypto_params.generate_private_key()
    private_int = private_key.private_numbers().x
    public_int = private_key.public_key().public_numbers().y
    return private_int, public_int


def compute_shared_secret(
    params: DHParameters,
    agent_private_int: int,
    manager_public_bytes: bytes,
) -> bytes:
    """Compute the DH shared secret.

    Computes ``manager_public ^ agent_private mod p`` and returns the result
    as a fixed-width big-endian byte string padded to the byte length of *p*.
    """
    p = params.p
    manager_public_int = bytes_to_int(manager_public_bytes)
    shared_int = pow(manager_public_int, agent_private_int, p)
    p_byte_len = (p.bit_length() + 7) // 8
    return int_to_bytes(shared_int, p_byte_len)


def derive_key(shared_secret: bytes, key_length: int) -> bytes:
    """Extract the *key_length* rightmost bytes of *shared_secret* as the new key.

    Per RFC 2786 §4.2: the new key is the ``n`` rightmost bits (bytes) of the
    shared secret, where ``n`` is determined by the target auth/priv protocol.
    """
    if key_length <= 0:
        return b""
    return shared_secret[-key_length:]
