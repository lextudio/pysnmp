import pytest
from pyasn1.type.namedtype import NamedType

from pysnmp.proto.rfc1155 import NetworkAddress, IpAddress, TypeCoercionHackMixIn


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

    t._verifyComponent(0, IpAddress("10.2.3.4"))


def test_verifyComponent_invalidIdx():
    t = TypeCoercionHackMixIn()
    t._componentType = [NamedType("internet", IpAddress("10.10.10.10"))]

    with pytest.raises(Exception):
        t._verifyComponent(1, IpAddress("10.2.3.4"))
