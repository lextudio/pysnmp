#
# This file is part of pysnmp software.
#
# Copyright (C) 2024, LeXtudio Inc. <support@lextudio.com>
# License: https://www.pysnmp.com/pysnmp/license.html
#
import socket
import warnings
from typing import Tuple

from pysnmp.carrier.asyncio.stream.base import StreamAsyncioProtocol
from pysnmp.carrier.base import AbstractTransportAddress

DOMAIN_NAME: Tuple[int, ...]
SNMP_TCP_DOMAIN: Tuple[int, ...]
DOMAIN_NAME = SNMP_TCP_DOMAIN = (1, 3, 6, 1, 6, 1, 3)


class TcpTransportAddress(tuple, AbstractTransportAddress):
    """TCP transport address."""

    pass


class TcpAsyncioTransport(StreamAsyncioProtocol):
    """TCP async transport."""

    SOCK_FAMILY = socket.AF_INET
    ADDRESS_TYPE = TcpTransportAddress


TcpTransport = TcpAsyncioTransport

deprecated_attributes = {
    "domainName": "DOMAIN_NAME",
    "snmpTCPDomain": "SNMP_TCP_DOMAIN",
}


def __getattr__(attr: str):
    if new_attr := deprecated_attributes.get(attr):
        warnings.warn(
            f"{attr} is deprecated. Please use {new_attr} instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return globals()[new_attr]
    raise AttributeError(f"module '{__name__}' has no attribute '{attr}'")
