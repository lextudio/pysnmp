import pytest
from pyasn1.type.namedtype import NamedType

from pysnmp.hlapi.v3arch.asyncio import ObjectIdentity, ObjectType, SnmpEngine
from pysnmp.proto.rfc1155 import NetworkAddress, IpAddress, TypeCoercionHackMixIn
from pysnmp.smi import view


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


def test_network_address_resolv():
    with SnmpEngine() as snmp_engine:
        mib_builder = snmp_engine.get_mib_builder()
        mib_view_controller = view.MibViewController(mib_builder)
        mib_builder.load_modules("RFC1213-MIB")
        object_type = ObjectType(
            ObjectIdentity("1.3.6.1.2.1.3.1.1.3.5.1.192.168.43.33")
        )
        resolved = object_type.resolve_with_mib(mib_view_controller)
        assert (
            resolved[0].prettyPrint()
            == '''RFC1213-MIB::atNetAddress.5."NetworkAddress:
 internet=192.168.43.33
"'''
        )
