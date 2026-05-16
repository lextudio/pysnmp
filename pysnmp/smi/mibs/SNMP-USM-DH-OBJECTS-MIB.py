#
# This file is part of pysnmp software.
#
# Copyright (c) 2024, LeXtudio Inc. <support@lextudio.com>
# License: https://www.pysnmp.com/pysnmp/license.html
#
# SNMP MIB module SNMP-USM-DH-OBJECTS-MIB
# Based on RFC 2786 — Diffie-Hellman USM Key Management Extensions
#
# IMPORTANT: customization — RFC 2786 DHKeyChange columns are implemented
# with full DH key exchange logic.
#

(Integer,
 OctetString,
 ObjectIdentifier) = mibBuilder.import_symbols(
    "ASN1",
    "Integer",
    "OctetString",
    "ObjectIdentifier")

(NamedValues,) = mibBuilder.import_symbols(
    "ASN1-ENUMERATION",
    "NamedValues")
(ConstraintsIntersection,
 ConstraintsUnion,
 SingleValueConstraint,
 ValueRangeConstraint,
 ValueSizeConstraint) = mibBuilder.import_symbols(
    "ASN1-REFINEMENT",
    "ConstraintsIntersection",
    "ConstraintsUnion",
    "SingleValueConstraint",
    "ValueRangeConstraint",
    "ValueSizeConstraint")

(SnmpAdminString,) = mibBuilder.import_symbols(
    "SNMP-FRAMEWORK-MIB",
    "SnmpAdminString")

(usmUserEntry,) = mibBuilder.import_symbols(
    "SNMP-USER-BASED-SM-MIB",
    "usmUserEntry")

(ModuleCompliance,
 NotificationGroup,
 ObjectGroup) = mibBuilder.import_symbols(
    "SNMPv2-CONF",
    "ModuleCompliance",
    "NotificationGroup",
    "ObjectGroup")

(Bits,
 Integer32,
 IpAddress,
 ModuleIdentity,
 MibIdentifier,
 ObjectIdentity,
 MibScalar,
 MibTable,
 MibTableRow,
 MibTableColumn,
 TimeTicks,
 Unsigned32,
 experimental,
 iso) = mibBuilder.import_symbols(
    "SNMPv2-SMI",
    "Bits",
    "Integer32",
    "IpAddress",
    "ModuleIdentity",
    "MibIdentifier",
    "ObjectIdentity",
    "MibScalar",
    "MibTable",
    "MibTableRow",
    "MibTableColumn",
    "TimeTicks",
    "Unsigned32",
    "experimental",
    "iso")

(DisplayString,
 PhysAddress,
 TextualConvention) = mibBuilder.import_symbols(
    "SNMPv2-TC",
    "DisplayString",
    "PhysAddress",
    "TextualConvention")

# IMPORTANT: customization — import DH core and SMI error types
from pysnmp.proto.secmod import rfc2786 as _dh_core
from pysnmp.smi import error as _smi_error

# MODULE-IDENTITY

snmpUsmDHObjectsMIB = ModuleIdentity(
    (1, 3, 6, 1, 3, 101)
)

# ---------------------------------------------------------------------------
# TEXTUAL-CONVENTIONS
# ---------------------------------------------------------------------------


class DHKeyChange(TextualConvention, OctetString):
    """Represents a DH key-change value (RFC 2786).

    On read: returns the agent's current DH public value for this user.
    On write: the manager provides (agent_current_public || manager_new_public);
    the agent verifies the first half, computes the shared secret, derives the
    new key from the rightmost N bytes, then rotates its own DH key pair.
    """
    status = "current"


# ---------------------------------------------------------------------------
# IMPORTANT: customization — per-user DH state and helpers
# ---------------------------------------------------------------------------

# Per-user DH agent state: inst_id_tuple -> (private_int, public_bytes)
_dh_agent_state: dict = {}

# Pending write state: inst_id_tuple -> (new_pub_bytes, new_key_bytes, new_priv_int)
_pending_dh: dict = {}

# Auth key sizes by auth-protocol OID tuple (RFC 3414, RFC 7860)
_AUTH_KEY_SIZES: dict = {
    (1, 3, 6, 1, 6, 3, 10, 1, 1, 2): 16,   # usmHMACMD5AuthProtocol
    (1, 3, 6, 1, 6, 3, 10, 1, 1, 3): 20,   # usmHMACSHAAuthProtocol
    (1, 3, 6, 1, 6, 3, 10, 1, 1, 4): 28,   # usmHMAC128SHA224AuthProtocol
    (1, 3, 6, 1, 6, 3, 10, 1, 1, 5): 32,   # usmHMAC192SHA256AuthProtocol
    (1, 3, 6, 1, 6, 3, 10, 1, 1, 6): 48,   # usmHMAC256SHA384AuthProtocol
    (1, 3, 6, 1, 6, 3, 10, 1, 1, 7): 64,   # usmHMAC384SHA512AuthProtocol
}

# Priv key sizes by priv-protocol OID tuple
_PRIV_KEY_SIZES: dict = {
    (1, 3, 6, 1, 6, 3, 10, 1, 2, 2): 16,           # usmDESPrivProtocol
    (1, 3, 6, 1, 6, 3, 10, 1, 2, 3): 32,           # usm3DESEDEPrivProtocol
    (1, 3, 6, 1, 6, 3, 10, 1, 2, 4): 16,           # usmAesCfb128Protocol
    (1, 3, 6, 1, 4, 1, 9, 12, 6, 1, 1): 24,        # AES-192 (Cisco ESO)
    (1, 3, 6, 1, 4, 1, 9, 12, 6, 1, 2): 32,        # AES-256 (Cisco ESO)
    # Blumenthal variants (same OIDs as above in some implementations)
}


def _get_dh_params():
    """Return current DH parameters from usmDHParameters (or Oakley Group 2 default)."""
    raw = bytes(usmDHParameters.syntax)
    if raw:
        try:
            return _dh_core.decode_parameters(raw)
        except Exception:
            pass
    return _dh_core.get_default_parameters()


def _ensure_user_dh_state(inst_id: tuple) -> tuple:
    """Lazily generate and cache a DH key pair for *inst_id*.

    Returns *(private_int, public_bytes)*.
    """
    if inst_id not in _dh_agent_state:
        params = _get_dh_params()
        private_int, public_int = _dh_core.generate_key_pair(params)
        p_byte_len = (params.p.bit_length() + 7) // 8
        public_bytes = _dh_core.int_to_bytes(public_int, p_byte_len)
        _dh_agent_state[inst_id] = (private_int, public_bytes)
    return _dh_agent_state[inst_id]


def _get_user_auth_protocol(inst_id: tuple) -> tuple:
    """Return the auth-protocol OID tuple for the user at *inst_id*."""
    try:
        (entry,) = mibBuilder.import_symbols("SNMP-USER-BASED-SM-MIB", "usmUserEntry")
        # usmUserAuthProtocol is column 5
        node = entry.getNode(entry.name + (5,) + inst_id)
        return tuple(node.syntax)
    except Exception:
        return ()


def _get_user_priv_protocol(inst_id: tuple) -> tuple:
    """Return the priv-protocol OID tuple for the user at *inst_id*."""
    try:
        (entry,) = mibBuilder.import_symbols("SNMP-USER-BASED-SM-MIB", "usmUserEntry")
        # usmUserPrivProtocol is column 8
        node = entry.getNode(entry.name + (8,) + inst_id)
        return tuple(node.syntax)
    except Exception:
        return ()


def _update_user_auth_key(inst_id: tuple, key_bytes: bytes) -> None:
    """Write *key_bytes* into pysnmpUsmKeyAuthLocalized (column 1) for *inst_id*."""
    try:
        (key_entry,) = mibBuilder.import_symbols("PYSNMP-USM-MIB", "pysnmpUsmKeyEntry")
        node = key_entry.getNode(key_entry.name + (1,) + inst_id)
        node.syntax = node.syntax.clone(key_bytes)
    except Exception:
        pass


def _update_user_priv_key(inst_id: tuple, key_bytes: bytes) -> None:
    """Write *key_bytes* into pysnmpUsmKeyPrivLocalized (column 2) for *inst_id*."""
    try:
        (key_entry,) = mibBuilder.import_symbols("PYSNMP-USM-MIB", "pysnmpUsmKeyEntry")
        node = key_entry.getNode(key_entry.name + (2,) + inst_id)
        node.syntax = node.syntax.clone(key_bytes)
    except Exception:
        pass


class DHKeyChangeColumn(MibTableColumn):
    """MibTableColumn implementing RFC 2786 DHKeyChange semantics.

    - On read: returns the agent's current DH public value for this user
      (lazily generating the key pair on first access).
    - On write: validates that the first half of the written value matches
      the current agent public, computes the shared secret, derives the new
      auth or priv key, rotates the agent DH key pair, and stores the new
      public value so subsequent reads return it.
    """

    # Subclasses set this to False for priv-key columns.
    _IS_AUTH: bool = True

    def _sync_public(self, name: tuple, **context) -> None:
        """Ensure the MibScalarInstance stores the current agent DH public value."""
        inst_id = name[len(self.name):]
        _, pub = _ensure_user_dh_state(inst_id)
        try:
            node = MibTableColumn.getBranch(self, name, **context)
            try:
                current = bytes(node.syntax)
                if current == pub:
                    return  # already up to date
            except Exception:
                pass  # schema object with no value — fall through to initialize
            node.syntax = node.syntax.clone(pub)
        except Exception:
            pass

    def readGet(self, varBind, **context):
        name, val = varBind
        self._sync_public(name, **context)
        return MibTableColumn.readGet(self, varBind, **context)

    def readTestNext(self, varBind, **context):
        name, val = varBind
        # Sync so that the value returned during a GETNEXT is also correct.
        try:
            self._sync_public(name, **context)
        except Exception:
            pass
        return MibTableColumn.readTestNext(self, varBind, **context)

    def writeTest(self, varBind, **context):  # noqa: N802
        name, val = varBind
        inst_id = name[len(self.name):]

        if val is not None:
            val_bytes = bytes(val)
            params = _get_dh_params()
            p_byte_len = (params.p.bit_length() + 7) // 8

            if len(val_bytes) != 2 * p_byte_len:
                raise _smi_error.WrongLengthError(name=name, idx=context.get("idx"))

            agent_pub = val_bytes[:p_byte_len]
            mgr_pub = val_bytes[p_byte_len:]

            _, current_pub = _ensure_user_dh_state(inst_id)
            if agent_pub != current_pub:
                raise _smi_error.WrongValueError(name=name, idx=context.get("idx"))

            # Compute DH shared secret and new key
            current_priv, _ = _dh_agent_state[inst_id]
            shared = _dh_core.compute_shared_secret(params, current_priv, mgr_pub)

            if self._IS_AUTH:
                proto = _get_user_auth_protocol(inst_id)
                key_size = _AUTH_KEY_SIZES.get(proto, 0)
            else:
                proto = _get_user_priv_protocol(inst_id)
                key_size = _PRIV_KEY_SIZES.get(proto, 0)

            new_key = _dh_core.derive_key(shared, key_size)

            # Pre-generate the next DH key pair
            new_priv, new_pub_int = _dh_core.generate_key_pair(params)
            new_pub_bytes = _dh_core.int_to_bytes(new_pub_int, p_byte_len)

            # Stash for writeCommit
            _pending_dh[inst_id] = (new_pub_bytes, new_key, new_priv)

            # Let the parent set __newSyntax = new_pub_bytes (for writeCommit)
            return MibTableColumn.writeTest(
                self, (name, val.__class__(new_pub_bytes)), **context
            )

        return MibTableColumn.writeTest(self, varBind, **context)

    def writeCommit(self, varBind, **context):  # noqa: N802
        name, val = varBind
        inst_id = name[len(self.name):]

        if inst_id in _pending_dh:
            new_pub_bytes, new_key, new_priv = _pending_dh[inst_id]
            # Apply the new key
            if new_key:
                if self._IS_AUTH:
                    _update_user_auth_key(inst_id, new_key)
                else:
                    _update_user_priv_key(inst_id, new_key)
            # Commit new DH state
            _dh_agent_state[inst_id] = (new_priv, new_pub_bytes)

        MibTableColumn.writeCommit(self, varBind, **context)

    def writeCleanup(self, varBind, **context):  # noqa: N802
        name, val = varBind
        inst_id = name[len(self.name):]
        _pending_dh.pop(inst_id, None)
        MibTableColumn.writeCleanup(self, varBind, **context)

    def writeUndo(self, varBind, **context):  # noqa: N802
        name, val = varBind
        inst_id = name[len(self.name):]
        _pending_dh.pop(inst_id, None)
        MibTableColumn.writeUndo(self, varBind, **context)


class _DHAuthKeyChangeColumn(DHKeyChangeColumn):
    _IS_AUTH = True


class _DHPrivKeyChangeColumn(DHKeyChangeColumn):
    _IS_AUTH = False


# ---------------------------------------------------------------------------
# MIB Managed Objects
# ---------------------------------------------------------------------------

usmDHKeyObjects = MibIdentifier((1, 3, 6, 1, 3, 101, 1))
usmDHPublicObjects = MibIdentifier((1, 3, 6, 1, 3, 101, 1, 1))

# usmDHParameters — holds PKCS#3-encoded DH group parameters.
# Default: Oakley Group 2 (RFC 2409) BER-encoded.
_default_dh_params = _dh_core.encode_parameters(
    _dh_core.get_default_parameters(),
    private_value_length=_dh_core.OAKLEY_GROUP2_PRIVATE_BITS,
)

usmDHParameters = MibScalar(
    (1, 3, 6, 1, 3, 101, 1, 1, 1),
    OctetString(_default_dh_params),
)
usmDHParameters.setMaxAccess("read-write")

# usmDHUserKeyTable — AUGMENTS usmUserTable

usmDHUserKeyTable = MibTable((1, 3, 6, 1, 3, 101, 1, 1, 2))

usmDHUserKeyEntry = MibTableRow((1, 3, 6, 1, 3, 101, 1, 1, 2, 1))

usmDHUserAuthKeyChange = _DHAuthKeyChangeColumn(
    (1, 3, 6, 1, 3, 101, 1, 1, 2, 1, 1),
    DHKeyChange(),
)
usmDHUserAuthKeyChange.setMaxAccess("read-create")

usmDHUserOwnAuthKeyChange = _DHAuthKeyChangeColumn(
    (1, 3, 6, 1, 3, 101, 1, 1, 2, 1, 2),
    DHKeyChange(),
)
usmDHUserOwnAuthKeyChange.setMaxAccess("read-create")

usmDHUserPrivKeyChange = _DHPrivKeyChangeColumn(
    (1, 3, 6, 1, 3, 101, 1, 1, 2, 1, 3),
    DHKeyChange(),
)
usmDHUserPrivKeyChange.setMaxAccess("read-create")

usmDHUserOwnPrivKeyChange = _DHPrivKeyChangeColumn(
    (1, 3, 6, 1, 3, 101, 1, 1, 2, 1, 4),
    DHKeyChange(),
)
usmDHUserOwnPrivKeyChange.setMaxAccess("read-create")

# Wire up AUGMENTS relationship
usmUserEntry.registerAugmentions(
    ("SNMP-USM-DH-OBJECTS-MIB", "usmDHUserKeyEntry")
)
usmDHUserKeyEntry.setIndexNames(*usmUserEntry.getIndexNames())

# usmDHKickstartTable — read-only bootstrap table

usmDHKickstartGroup = MibIdentifier((1, 3, 6, 1, 3, 101, 1, 2))

usmDHKickstartTable = MibTable((1, 3, 6, 1, 3, 101, 1, 2, 1))

usmDHKickstartEntry = MibTableRow((1, 3, 6, 1, 3, 101, 1, 2, 1, 1))
usmDHKickstartEntry.setIndexNames(
    (0, "SNMP-USM-DH-OBJECTS-MIB", "usmDHKickstartIndex"),
)


class _UsmDHKickstartIndex_Type(Integer32):
    subtypeSpec = Integer32.subtypeSpec + ConstraintsUnion(
        ValueRangeConstraint(1, 2147483647),
    )


usmDHKickstartIndex = MibTableColumn(
    (1, 3, 6, 1, 3, 101, 1, 2, 1, 1, 1),
    _UsmDHKickstartIndex_Type(),
)
usmDHKickstartIndex.setMaxAccess("not-accessible")

usmDHKickstartMyPublic = MibTableColumn(
    (1, 3, 6, 1, 3, 101, 1, 2, 1, 1, 2),
    OctetString(),
)
usmDHKickstartMyPublic.setMaxAccess("read-only")

usmDHKickstartMgrPublic = MibTableColumn(
    (1, 3, 6, 1, 3, 101, 1, 2, 1, 1, 3),
    OctetString(),
)
usmDHKickstartMgrPublic.setMaxAccess("read-only")

usmDHKickstartSecurityName = MibTableColumn(
    (1, 3, 6, 1, 3, 101, 1, 2, 1, 1, 4),
    SnmpAdminString(),
)
usmDHKickstartSecurityName.setMaxAccess("read-only")

# Conformance

usmDHKeyConformance = MibIdentifier((1, 3, 6, 1, 3, 101, 2))
usmDHKeyMIBCompliances = MibIdentifier((1, 3, 6, 1, 3, 101, 2, 1))
usmDHKeyMIBGroups = MibIdentifier((1, 3, 6, 1, 3, 101, 2, 2))

usmDHKeyMIBBasicGroup = ObjectGroup((1, 3, 6, 1, 3, 101, 2, 2, 1))
usmDHKeyMIBBasicGroup.setObjects(
    ("SNMP-USM-DH-OBJECTS-MIB", "usmDHUserAuthKeyChange"),
    ("SNMP-USM-DH-OBJECTS-MIB", "usmDHUserOwnAuthKeyChange"),
    ("SNMP-USM-DH-OBJECTS-MIB", "usmDHUserPrivKeyChange"),
    ("SNMP-USM-DH-OBJECTS-MIB", "usmDHUserOwnPrivKeyChange"),
)

usmDHKeyParamGroup = ObjectGroup((1, 3, 6, 1, 3, 101, 2, 2, 2))
usmDHKeyParamGroup.setObjects(
    ("SNMP-USM-DH-OBJECTS-MIB", "usmDHParameters"),
)

usmDHKeyKickstartGroup = ObjectGroup((1, 3, 6, 1, 3, 101, 2, 2, 3))
usmDHKeyKickstartGroup.setObjects(
    ("SNMP-USM-DH-OBJECTS-MIB", "usmDHKickstartMyPublic"),
    ("SNMP-USM-DH-OBJECTS-MIB", "usmDHKickstartMgrPublic"),
    ("SNMP-USM-DH-OBJECTS-MIB", "usmDHKickstartSecurityName"),
)

usmDHKeyMIBCompliance = ModuleCompliance((1, 3, 6, 1, 3, 101, 2, 1, 1))
usmDHKeyMIBCompliance.setObjects(
    ("SNMP-USM-DH-OBJECTS-MIB", "usmDHKeyMIBBasicGroup"),
    ("SNMP-USM-DH-OBJECTS-MIB", "usmDHKeyParamGroup"),
    ("SNMP-USM-DH-OBJECTS-MIB", "usmDHKeyKickstartGroup"),
)

# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------

mibBuilder.export_symbols(
    "SNMP-USM-DH-OBJECTS-MIB",
    **{
        "DHKeyChange": DHKeyChange,
        "snmpUsmDHObjectsMIB": snmpUsmDHObjectsMIB,
        "usmDHKeyObjects": usmDHKeyObjects,
        "usmDHPublicObjects": usmDHPublicObjects,
        "usmDHParameters": usmDHParameters,
        "usmDHUserKeyTable": usmDHUserKeyTable,
        "usmDHUserKeyEntry": usmDHUserKeyEntry,
        "usmDHUserAuthKeyChange": usmDHUserAuthKeyChange,
        "usmDHUserOwnAuthKeyChange": usmDHUserOwnAuthKeyChange,
        "usmDHUserPrivKeyChange": usmDHUserPrivKeyChange,
        "usmDHUserOwnPrivKeyChange": usmDHUserOwnPrivKeyChange,
        "usmDHKickstartGroup": usmDHKickstartGroup,
        "usmDHKickstartTable": usmDHKickstartTable,
        "usmDHKickstartEntry": usmDHKickstartEntry,
        "usmDHKickstartIndex": usmDHKickstartIndex,
        "usmDHKickstartMyPublic": usmDHKickstartMyPublic,
        "usmDHKickstartMgrPublic": usmDHKickstartMgrPublic,
        "usmDHKickstartSecurityName": usmDHKickstartSecurityName,
        "usmDHKeyConformance": usmDHKeyConformance,
        "usmDHKeyMIBCompliances": usmDHKeyMIBCompliances,
        "usmDHKeyMIBCompliance": usmDHKeyMIBCompliance,
        "usmDHKeyMIBGroups": usmDHKeyMIBGroups,
        "usmDHKeyMIBBasicGroup": usmDHKeyMIBBasicGroup,
        "usmDHKeyParamGroup": usmDHKeyParamGroup,
        "usmDHKeyKickstartGroup": usmDHKeyKickstartGroup,
    }
)
