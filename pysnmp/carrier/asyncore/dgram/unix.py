#
# This file is part of pysnmp software.
#
# Copyright (c) 2005-2020, Ilya Etingof <etingof@gmail.com>
# License: https://www.pysnmp.com/pysnmp/license.html
#
import os
import random

try:
    from socket import AF_UNIX

except ImportError:
    AF_UNIX = None

from pysnmp.carrier.base import AbstractTransportAddress
from pysnmp.carrier.asyncore.dgram.base import DgramSocketTransport

DOMAIN_NAME = SNMP_LOCAL_DOMAIN = (1, 3, 6, 1, 2, 1, 100, 1, 13)

random.seed()


class UnixTransportAddress(str, AbstractTransportAddress):
    pass


class UnixSocketTransport(DgramSocketTransport):
    SOCK_FAMILY = AF_UNIX
    ADDRESS_TYPE = UnixTransportAddress
    _iface = ''

    def openClientMode(self, iface=None):
        if iface is None:
            # UNIX domain sockets must be explicitly bound
            iface = ''

            while len(iface) < 8:
                iface += chr(random.randrange(65, 91))
                iface += chr(random.randrange(97, 123))

            iface = os.path.join(os.path.sep, 'tmp', 'pysnmp', iface)

        if os.path.exists(iface):
            os.remove(iface)

        DgramSocketTransport.openClientMode(self, iface)

        self._iface = iface

        return self

    def openServerMode(self, iface):
        DgramSocketTransport.openServerMode(self, iface)
        self._iface = iface
        return self

    def closeTransport(self):
        DgramSocketTransport.closeTransport(self)

        try:
            os.remove(self._iface)

        except OSError:
            pass


UnixTransport = UnixSocketTransport

# Compatibility stub
UnixDgramSocketTransport = UnixSocketTransport
