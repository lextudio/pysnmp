#
# This file is part of pysnmp software.
#
# Copyright (c) 2005-2020, Ilya Etingof <etingof@gmail.com>
# License: https://www.pysnmp.com/pysnmp/license.html
#
import socket
from typing import Tuple
from pysnmp.carrier.base import AbstractTransportAddress
from pysnmp.carrier.asyncio.dgram.base import DgramAsyncioProtocol
from pysnmp.carrier.base import AbstractTransportAddress

DOMAIN_NAME: Tuple[int, ...]
SNMP_UDP6_DOMAIN: Tuple[int, ...]
DOMAIN_NAME = SNMP_UDP6_DOMAIN = (1, 3, 6, 1, 2, 1, 100, 1, 2)


class Udp6TransportAddress(tuple, AbstractTransportAddress):
    pass


class Udp6AsyncioTransport(DgramAsyncioProtocol):
    SOCK_FAMILY = socket.has_ipv6 and socket.AF_INET6 or None
    ADDRESS_TYPE = Udp6TransportAddress

    def normalizeAddress(self, transportAddress):
        if "%" in transportAddress[0]:  # strip zone ID
            return self.ADDRESS_TYPE(
                (
                    transportAddress[0].split("%")[0],
                    transportAddress[1],
                    0,  # flowinfo
                    0,
                )
            )  # scopeid
        else:
            return self.ADDRESS_TYPE((transportAddress[0], transportAddress[1], 0, 0))


Udp6Transport = Udp6AsyncioTransport
