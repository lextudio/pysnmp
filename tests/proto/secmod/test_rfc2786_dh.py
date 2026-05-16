"""
Tests for RFC 2786 — Diffie-Hellman USM Key Management.

Covers:
  - rfc2786 DH core: key generation, shared secret computation, key derivation,
    parameter encoding/decoding (symmetry of both sides of the exchange).
  - SNMP-USM-DH-OBJECTS-MIB: usmDHParameters default, usmDHUserAuthKeyChange
    column returns agent public on read and correctly updates the auth key on
    a simulated manager SET.
"""

import pytest

from pysnmp.proto.secmod import rfc2786 as dh
from pysnmp.entity import engine, config
from pysnmp.smi import builder, view


# ---------------------------------------------------------------------------
# rfc2786 module unit tests
# ---------------------------------------------------------------------------


class TestDhCore:
    def test_generate_key_pair_returns_integers(self):
        params = dh.get_default_parameters()
        priv, pub = dh.generate_key_pair(params)
        assert isinstance(priv, int) and priv > 0
        assert isinstance(pub, int) and pub > 0

    def test_shared_secret_symmetric(self):
        """Both sides of a DH exchange must compute the same shared secret."""
        params = dh.get_default_parameters()
        p_len = (params.p.bit_length() + 7) // 8

        priv_a, pub_a = dh.generate_key_pair(params)
        priv_b, pub_b = dh.generate_key_pair(params)

        pub_a_bytes = dh.int_to_bytes(pub_a, p_len)
        pub_b_bytes = dh.int_to_bytes(pub_b, p_len)

        shared_a = dh.compute_shared_secret(params, priv_a, pub_b_bytes)
        shared_b = dh.compute_shared_secret(params, priv_b, pub_a_bytes)

        assert shared_a == shared_b

    def test_derive_key_rightmost_bytes(self):
        secret = bytes(range(32))
        assert dh.derive_key(secret, 16) == bytes(range(16, 32))
        assert dh.derive_key(secret, 20) == bytes(range(12, 32))

    def test_int_to_bytes_roundtrip(self):
        for n in (0, 1, 255, 256, 2**128 - 1):
            b = dh.int_to_bytes(n)
            assert dh.bytes_to_int(b) == n

    def test_int_to_bytes_padded(self):
        b = dh.int_to_bytes(1, 16)
        assert len(b) == 16
        assert b[-1] == 1

    def test_parameter_encoding_roundtrip(self):
        params = dh.get_default_parameters()
        encoded = dh.encode_parameters(params, dh.OAKLEY_GROUP2_PRIVATE_BITS)
        decoded = dh.decode_parameters(encoded)
        assert decoded.p == params.p
        assert decoded.g == params.g

    def test_default_parameters_are_oakley_group2(self):
        params = dh.get_default_parameters()
        assert params.p == dh.OAKLEY_GROUP2_PRIME
        assert params.g == dh.OAKLEY_GROUP2_GENERATOR


# ---------------------------------------------------------------------------
# MIB / end-to-end tests
# ---------------------------------------------------------------------------


def _make_usm_engine_with_sha_user():
    """Create a SnmpEngine with a SHA-auth SNMPv3 user and load the DH MIB.

    The DH MIB must be loaded BEFORE add_v3_user so that when the usmUserEntry
    row is created, the AUGMENTS mechanism fires and creates the DHKeyChange
    column instances for the new user.
    """
    snmpEngine = engine.SnmpEngine()
    snmpEngine.get_mib_builder().load_modules("SNMP-USM-DH-OBJECTS-MIB")
    config.add_v3_user(
        snmpEngine,
        userName="testUser",
        authKey=b"authpassword",
        authProtocol=config.USM_AUTH_HMAC96_SHA,
        privKey=b"privpassword",
        privProtocol=config.USM_PRIV_CBC56_DES,
    )
    return snmpEngine


class TestDhMib:
    def test_usm_dh_parameters_has_default(self):
        snmpEngine = _make_usm_engine_with_sha_user()
        (usmDHParameters,) = snmpEngine.get_mib_builder().import_symbols(
            "SNMP-USM-DH-OBJECTS-MIB", "usmDHParameters"
        )
        raw = bytes(usmDHParameters.syntax)
        assert len(raw) > 0
        # Must decode to Oakley Group 2
        params = dh.decode_parameters(raw)
        assert params.p == dh.OAKLEY_GROUP2_PRIME

    def test_auth_key_column_returns_agent_public_on_read(self):
        """Reading usmDHUserAuthKeyChange must return a non-empty public value."""
        snmpEngine = _make_usm_engine_with_sha_user()
        mb = snmpEngine.get_mib_builder()

        (usmUserEntry,) = mb.import_symbols("SNMP-USER-BASED-SM-MIB", "usmUserEntry")
        (snmpEngineID,) = mb.import_symbols("__SNMP-FRAMEWORK-MIB", "snmpEngineID")
        engine_id = snmpEngineID.syntax

        tbl_idx = usmUserEntry.getInstIdFromIndices(engine_id, "testUser")

        (col,) = mb.import_symbols("SNMP-USM-DH-OBJECTS-MIB", "usmDHUserAuthKeyChange")

        oid = col.name + tbl_idx
        name, val = col.readGet((oid, col.syntax), snmpEngine=snmpEngine)
        pub_bytes = bytes(val)

        p_len = (dh.OAKLEY_GROUP2_PRIME.bit_length() + 7) // 8
        assert len(pub_bytes) == p_len
        assert any(b != 0 for b in pub_bytes)

    def test_dh_auth_key_exchange_updates_key(self):
        """
        Simulate a manager performing a DH auth key change:
          1. Read agent's current public value.
          2. Generate manager key pair.
          3. SET column with (agent_pub || manager_pub).
          4. Verify the localized auth key in pysnmpUsmKeyEntry changed.
        """
        snmpEngine = _make_usm_engine_with_sha_user()
        mb = snmpEngine.get_mib_builder()

        (usmUserEntry,) = mb.import_symbols("SNMP-USER-BASED-SM-MIB", "usmUserEntry")
        (snmpEngineID,) = mb.import_symbols("__SNMP-FRAMEWORK-MIB", "snmpEngineID")
        engine_id = snmpEngineID.syntax
        tbl_idx = usmUserEntry.getInstIdFromIndices(engine_id, "testUser")

        (col,) = mb.import_symbols("SNMP-USM-DH-OBJECTS-MIB", "usmDHUserAuthKeyChange")
        (key_entry,) = mb.import_symbols("PYSNMP-USM-MIB", "pysnmpUsmKeyEntry")

        oid = col.name + tbl_idx

        # Step 1: read agent public
        _, val = col.readGet((oid, col.syntax), snmpEngine=snmpEngine)
        agent_pub_bytes = bytes(val)

        # Step 2: generate manager key pair
        params = dh.get_default_parameters()
        mgr_priv, mgr_pub = dh.generate_key_pair(params)
        p_len = (params.p.bit_length() + 7) // 8
        mgr_pub_bytes = dh.int_to_bytes(mgr_pub, p_len)

        # Record original auth key
        orig_key = bytes(key_entry.getNode(key_entry.name + (1,) + tbl_idx).syntax)

        # Step 3: perform SET (writeTest + writeCommit + writeCleanup)
        set_value = col.syntax.clone(agent_pub_bytes + mgr_pub_bytes)
        varBind = (oid, set_value)

        col.writeTest(varBind, snmpEngine=snmpEngine)
        col.writeCommit(varBind, snmpEngine=snmpEngine)
        col.writeCleanup(varBind, snmpEngine=snmpEngine)

        # Step 4: verify auth key changed
        new_key = bytes(key_entry.getNode(key_entry.name + (1,) + tbl_idx).syntax)
        assert new_key != orig_key
        assert len(new_key) == 20  # SHA-1 auth key = 20 bytes

        # Step 5: verify manager computes the same new key
        shared = dh.compute_shared_secret(params, mgr_priv, agent_pub_bytes)
        expected_key = dh.derive_key(shared, 20)
        assert new_key == expected_key

    def test_wrong_agent_pub_raises(self):
        """SET with mismatched agent public must raise WrongValueError."""
        from pysnmp.smi.error import WrongValueError

        snmpEngine = _make_usm_engine_with_sha_user()
        mb = snmpEngine.get_mib_builder()

        (usmUserEntry,) = mb.import_symbols("SNMP-USER-BASED-SM-MIB", "usmUserEntry")
        (snmpEngineID,) = mb.import_symbols("__SNMP-FRAMEWORK-MIB", "snmpEngineID")
        engine_id = snmpEngineID.syntax
        tbl_idx = usmUserEntry.getInstIdFromIndices(engine_id, "testUser")

        (col,) = mb.import_symbols("SNMP-USM-DH-OBJECTS-MIB", "usmDHUserAuthKeyChange")
        oid = col.name + tbl_idx

        # Initialize DH state by reading first
        col.readGet((oid, col.syntax), snmpEngine=snmpEngine)

        params = dh.get_default_parameters()
        p_len = (params.p.bit_length() + 7) // 8

        # Wrong agent pub (all zeros) + valid manager pub
        wrong_agent_pub = b"\x00" * p_len
        _, mgr_pub = dh.generate_key_pair(params)
        mgr_pub_bytes = dh.int_to_bytes(mgr_pub, p_len)

        set_value = col.syntax.clone(wrong_agent_pub + mgr_pub_bytes)
        with pytest.raises(WrongValueError):
            col.writeTest((oid, set_value), snmpEngine=snmpEngine)

    def test_wrong_length_raises(self):
        """SET with wrong-length value must raise WrongLengthError."""
        from pysnmp.smi.error import WrongLengthError

        snmpEngine = _make_usm_engine_with_sha_user()
        mb = snmpEngine.get_mib_builder()

        (usmUserEntry,) = mb.import_symbols("SNMP-USER-BASED-SM-MIB", "usmUserEntry")
        (snmpEngineID,) = mb.import_symbols("__SNMP-FRAMEWORK-MIB", "snmpEngineID")
        engine_id = snmpEngineID.syntax
        tbl_idx = usmUserEntry.getInstIdFromIndices(engine_id, "testUser")

        (col,) = mb.import_symbols("SNMP-USM-DH-OBJECTS-MIB", "usmDHUserAuthKeyChange")
        oid = col.name + tbl_idx

        set_value = col.syntax.clone(b"\x01\x02\x03")  # too short
        with pytest.raises(WrongLengthError):
            col.writeTest((oid, set_value), snmpEngine=snmpEngine)

    def test_second_read_returns_same_public_after_no_write(self):
        """Two consecutive reads must return the same public value."""
        snmpEngine = _make_usm_engine_with_sha_user()
        mb = snmpEngine.get_mib_builder()

        (usmUserEntry,) = mb.import_symbols("SNMP-USER-BASED-SM-MIB", "usmUserEntry")
        (snmpEngineID,) = mb.import_symbols("__SNMP-FRAMEWORK-MIB", "snmpEngineID")
        engine_id = snmpEngineID.syntax
        tbl_idx = usmUserEntry.getInstIdFromIndices(engine_id, "testUser")

        (col,) = mb.import_symbols("SNMP-USM-DH-OBJECTS-MIB", "usmDHUserAuthKeyChange")
        oid = col.name + tbl_idx

        _, val1 = col.readGet((oid, col.syntax), snmpEngine=snmpEngine)
        _, val2 = col.readGet((oid, col.syntax), snmpEngine=snmpEngine)

        assert bytes(val1) == bytes(val2)

    def test_read_after_write_returns_new_public(self):
        """After a successful key change, reading the column returns the NEW public."""
        snmpEngine = _make_usm_engine_with_sha_user()
        mb = snmpEngine.get_mib_builder()

        (usmUserEntry,) = mb.import_symbols("SNMP-USER-BASED-SM-MIB", "usmUserEntry")
        (snmpEngineID,) = mb.import_symbols("__SNMP-FRAMEWORK-MIB", "snmpEngineID")
        engine_id = snmpEngineID.syntax
        tbl_idx = usmUserEntry.getInstIdFromIndices(engine_id, "testUser")

        (col,) = mb.import_symbols("SNMP-USM-DH-OBJECTS-MIB", "usmDHUserAuthKeyChange")
        oid = col.name + tbl_idx

        _, val_before = col.readGet((oid, col.syntax), snmpEngine=snmpEngine)
        agent_pub = bytes(val_before)

        params = dh.get_default_parameters()
        p_len = (params.p.bit_length() + 7) // 8
        _, mgr_pub = dh.generate_key_pair(params)
        mgr_pub_bytes = dh.int_to_bytes(mgr_pub, p_len)

        set_value = col.syntax.clone(agent_pub + mgr_pub_bytes)
        col.writeTest((oid, set_value), snmpEngine=snmpEngine)
        col.writeCommit((oid, set_value), snmpEngine=snmpEngine)
        col.writeCleanup((oid, set_value), snmpEngine=snmpEngine)

        _, val_after = col.readGet((oid, col.syntax), snmpEngine=snmpEngine)
        assert bytes(val_after) != agent_pub  # new public after key rotation
