#
# This file is part of pysnmp software.
#
# Copyright (c) 2005-2020, Ilya Etingof <etingof@gmail.com>
# License: https://www.pysnmp.com/pysnmp/license.html
#
from typing import Tuple


from pysnmp import error
from pysnmp.carrier.base import AbstractTransport, AbstractTransportAddress
from pysnmp.entity.engine import SnmpEngine

__all__ = []


class AbstractTransportTarget:
    retries: int
    timeout: float
    transport: "AbstractTransport | None"
    transportAddr: Tuple[str, int]

    TRANSPORT_DOMAIN = None
    PROTO_TRANSPORT = AbstractTransport

    def __init__(
        self,
        transportAddr: Tuple,
        timeout: float = 1,
        retries: int = 5,
        tagList=b"",
    ):
        self.transportAddr = self._resolveAddr(transportAddr)
        self.timeout = timeout
        self.retries = retries
        self.tagList = tagList
        self.iface = None
        self.transport = None

    def __repr__(self):
        return "{}({!r}, timeout={!r}, retries={!r}, tagList={!r})".format(
            self.__class__.__name__,
            self.transportAddr,
            self.timeout,
            self.retries,
            self.tagList,
        )

    def getTransportInfo(self):
        return self.TRANSPORT_DOMAIN, self.transportAddr

    def setLocalAddress(self, iface):
        """Set source address.

        Parameters
        ----------
        iface : tuple
            Indicates network address of a local interface from which SNMP packets will be originated.
            Format is the same as of `transportAddress`.

        Returns
        -------
            self

        """
        self.iface = iface
        return self

    def openClientMode(self):
        self.transport = self.PROTO_TRANSPORT().openClientMode(self.iface)
        return self.transport

    def verifyDispatcherCompatibility(self, snmpEngine: SnmpEngine):
        if not self.PROTO_TRANSPORT.isCompatibleWithDispatcher(
            snmpEngine.transportDispatcher
        ):
            raise error.PySnmpError(
                "Transport {!r} is not compatible with dispatcher {!r}".format(
                    self.PROTO_TRANSPORT, snmpEngine.transportDispatcher
                )
            )

    def _resolveAddr(self, transportAddr: Tuple) -> Tuple[str, int]:
        raise NotImplementedError()
