import pytest
from pyasn1.type.namedtype import NamedType

from pysnmp.hlapi.v3arch.asyncio import ObjectIdentity, ObjectType, SnmpEngine
from pysnmp.proto.rfc1155 import NetworkAddress, IpAddress, TypeCoercionHackMixIn
from pysnmp.smi import builder, compiler, view


def test_clone_none():
    n = NetworkAddress()

    assert n.clone().prettyPrint() == n.prettyPrint()


def test_clone_NetworkAddress():
    n = NetworkAddress()

    assert n.clone(n.clone("10.10.10.10")).getName() == "internet"


def test_clone_IpAddress():
    ip = IpAddress("10.10.10.10")
    n = NetworkAddress()

    assert n.clone(ip).getName() == "internet"


def test_clone_string():
    n = NetworkAddress()

    assert n.clone("10.10.10.10").getName() == "internet"


def test_verifyComponent_normal():
    t = TypeCoercionHackMixIn()
    t._componentType = [NamedType("internet", IpAddress("10.10.10.10"))]

    t._verify_component(0, IpAddress("10.2.3.4"))


def test_verifyComponent_invalidIdx():
    t = TypeCoercionHackMixIn()
    t._componentType = [NamedType("internet", IpAddress("10.10.10.10"))]

    with pytest.raises(Exception):
        t._verify_component(1, IpAddress("10.2.3.4"))


def test_inet_address_ipv4_resolv():
    """Regression test for issue #211: InetAddress IPv4 index uses length-prefix encoding."""
    mib_builder = builder.MibBuilder()
    compiler.addMibCompiler(mib_builder)
    mib_view_controller = view.MibViewController(mib_builder)
    mib_builder.load_modules("TCP-MIB")
    object_type = ObjectType(ObjectIdentity("1.3.6.1.2.1.6.20.1.4.1.4.127.0.0.1.2002"))
    resolved = object_type.resolve_with_mib(mib_view_controller)
    assert (
        resolved[0].prettyPrint() == 'TCP-MIB::tcpListenerProcess.ipv4."127.0.0.1".2002'
    )


def test_inet_address_ipv6_resolv():
    """InetAddress IPv6 index also uses length-prefix encoding (16 bytes)."""
    mib_builder = builder.MibBuilder()
    compiler.addMibCompiler(mib_builder)
    mib_view_controller = view.MibViewController(mib_builder)
    mib_builder.load_modules("TCP-MIB")
    # InetAddressType=2 (ipv6), length=16, ::1, port=2002
    object_type = ObjectType(
        ObjectIdentity("1.3.6.1.2.1.6.20.1.4.2.16.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.1.2002")
    )
    resolved = object_type.resolve_with_mib(mib_view_controller)
    assert (
        resolved[0].prettyPrint()
        == 'TCP-MIB::tcpListenerProcess.ipv6."00:00:00:00:00:00:00:01".2002'
    )


def test_inet_address_roundtrip():
    """Parsing and formatting an InetAddress OID suffix must be symmetric."""
    mib_builder = builder.MibBuilder()
    compiler.addMibCompiler(mib_builder)
    mib_builder.load_modules("TCP-MIB")
    (tcp_listener_entry,) = mib_builder.import_symbols("TCP-MIB", "tcpListenerEntry")

    # OID suffix: InetAddressType=1 (ipv4), length=4, 127.0.0.1, port=2002
    inst_id = (1, 4, 127, 0, 0, 1, 2002)
    indices = tcp_listener_entry.getIndicesFromInstId(inst_id)
    roundtripped = tcp_listener_entry.getInstIdFromIndices(*indices)
    assert roundtripped == inst_id


def test_fixed_length_index_no_length_prefix():
    """Fixed-length OctetString indices (e.g. MacAddress) must NOT have a length prefix."""
    mib_builder = builder.MibBuilder()
    (MibTableRow,) = mib_builder.import_symbols("SNMPv2-SMI", "MibTableRow")
    (MacAddress,) = mib_builder.import_symbols("SNMPv2-TC", "MacAddress")

    row = MibTableRow((1, 3, 6, 1))
    mac_bytes = bytes([0x00, 0x1E, 0x48, 0x1E, 0x1C, 0x00])

    # Parsing: 6 raw sub-OIDs, no leading length byte
    oid_suffix = (0x00, 0x1E, 0x48, 0x1E, 0x1C, 0x00)
    parsed, remainder = row.setFromName(MacAddress(), oid_suffix)
    assert remainder == ()
    assert parsed.asNumbers() == oid_suffix

    # Formatting: must produce 6 sub-OIDs with no length prefix
    formatted = row.getAsName(MacAddress().clone(mac_bytes))
    assert formatted == oid_suffix


def test_network_address_resolv():
    """
    etingof/pysnmp#352: NetworkAddress index must prettyPrint as a plain IP
    address string, not as a pyasn1 CHOICE dump with newlines.
    """
    with SnmpEngine() as snmp_engine:
        mib_builder = snmp_engine.get_mib_builder()
        mib_view_controller = view.MibViewController(mib_builder)
        mib_builder.load_modules("RFC1213-MIB")
        object_type = ObjectType(
            ObjectIdentity("1.3.6.1.2.1.3.1.1.3.5.1.192.168.43.33")
        )
        resolved = object_type.resolve_with_mib(mib_view_controller)
        assert (
            resolved[0].prettyPrint() == 'RFC1213-MIB::atNetAddress.5."192.168.43.33"'
        )


def test_network_address_pretty_print():
    """
    etingof/pysnmp#352: NetworkAddress.prettyPrint() must return the plain IP
    address, not the pyasn1 CHOICE verbose dump.
    """
    na = NetworkAddress()
    na["internet"] = IpAddress("10.0.0.1")
    assert na.prettyPrint() == "10.0.0.1"
