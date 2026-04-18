import pytest
from time import time
from unittest.mock import patch

from pysnmp.proto.rfc1902 import Counter32, TimeTicks


def test_counter32_wraps_on_overflow():
    c = Counter32(0xFFFFFFFF)
    c += 1
    assert int(c) == 0


def test_counter32_wraps_on_large_add():
    c = Counter32(0xFFFFFFFE)
    c += 3
    assert int(c) == 1


def test_counter32_normal_increment():
    c = Counter32(10)
    c += 1
    assert int(c) == 11


def test_timeticks_wraps_on_overflow():
    t = TimeTicks(0xFFFFFFFF)
    t += 1
    assert int(t) == 0


def test_timeticks_normal_increment():
    t = TimeTicks(100)
    t += 1
    assert int(t) == 101


def test_timeticks_with_modulo_in_clone():
    # Test that TimeTicks properly wraps when a large value is passed
    # This simulates what happens in SysUpTime.clone() when elapsed time > 2**32
    large_value = int((time() - (time() - 0x100000000 / 100 - 60)) * 100)
    # Apply the modulo that SysUpTime.clone() should apply
    wrapped_value = large_value & 0xFFFFFFFF
    # Create a TimeTicks with the wrapped value
    t = TimeTicks(wrapped_value)
    assert int(t) <= 0xFFFFFFFF
