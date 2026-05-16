import importlib
import socket
import sys


def test_sockfix_defines_ipv6_transparent_when_missing(monkeypatch):
    """Ensure the carrier sockfix adds IPV6_TRANSPARENT when the socket module lacks it."""
    monkeypatch.delattr(socket, "IPV6_TRANSPARENT", raising=False)

    module_name = "pysnmp.carrier.sockfix"
    if module_name in sys.modules:
        del sys.modules[module_name]

    sockfix = importlib.import_module(module_name)

    assert hasattr(socket, "IPV6_TRANSPARENT")
    assert socket.IPV6_TRANSPARENT == 75
    assert sockfix.SYMBOLS["IPV6_TRANSPARENT"] == 75


def test_sockfix_does_not_override_existing_ipv6_transparent(monkeypatch):
    """Ensure existing IPV6_TRANSPARENT values are preserved when loading sockfix."""
    monkeypatch.setattr(socket, "IPV6_TRANSPARENT", 0xBEEF, raising=False)

    module_name = "pysnmp.carrier.sockfix"
    if module_name in sys.modules:
        del sys.modules[module_name]

    importlib.import_module(module_name)

    assert socket.IPV6_TRANSPARENT == 0xBEEF
