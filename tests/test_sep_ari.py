import pytest

from pysnmp.proto.rfc1902 import Bits


def test_prettyIn_list_valid():
    Fruit = Bits.withNamedBits(apple=0, orange=1, peach=2)

    assert Fruit().prettyIn(["apple"]) == b"\x80"
    assert Fruit().prettyIn(["orange"]) == b"\x40"
    assert Fruit().prettyIn(["peach"]) == b"\x20"

def test_prettyIn_list_multiple_valid():
    Fruit = Bits.withNamedBits(apple=0, orange=1, peach=2)

    assert Fruit().prettyIn(["peach", "apple"]) == b"\xA0"

def test_prettyIn_list_invalid():
    Fruit = Bits.withNamedBits(apple=0, orange=1, peach=2)

    with pytest.raises(Exception):
        Fruit().prettyIn(["banana"])

def test_prettyIn_multiple_octets():
    Fruit = Bits.withNamedBits(apple=0,
                               orange=1,
                               peach=2,
                               banana=3,
                               watermelon=4,
                               strawberry=5,
                               mango=6,
                               lemon=7,
                               cherry=8)

    assert len(Fruit().prettyIn(["cherry"])) > 1

def test_prettyOut_valid():
    Fruit = Bits.withNamedBits(apple=0, orange=1, peach=2)

    assert Fruit().prettyOut(b"\x20") == "peach"
    assert Fruit().prettyOut(b"\x40") == "orange"
    assert Fruit().prettyOut(b"\x80") == "apple"


def test_prettyOut_invalid():
    Fruit = Bits.withNamedBits(apple=0, orange=1, peach=2)

    assert Fruit().prettyOut(b"\x01").startswith("Unknown")
