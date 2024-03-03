#
# This file is part of pysnmp software.
#
# Copyright (c) 2005-2019, Ilya Etingof <etingof@gmail.com>
# License: https://www.pysnmp.com/pysnmp/license.html
#
from typing import Any, Callable
from pysnmp.carrier import error
from typing import Callable


class TimerCallable:
    __cbFun: Callable
    __nextCall: float
    __callInterval: float

    def __init__(self, cbFun: Callable, callInterval: float):
        self.__cbFun = cbFun
        self.__callInterval = callInterval
        self.__nextCall = 0

    def __call__(self, timeNow: float):
        if self.__nextCall <= timeNow:
            self.__cbFun(timeNow)
            self.__nextCall = timeNow + self.__callInterval

    def __eq__(self, cbFun: Callable):
        return self.__cbFun == cbFun

    def __ne__(self, cbFun: Callable):
        return self.__cbFun != cbFun

    @property
    def interval(self):
        return self.__callInterval

    @interval.setter
    def interval(self, callInterval: float):
        self.__callInterval = callInterval


class AbstractTransportAddress:
    _localAddress = None

    def setLocalAddress(self, s):
        self._localAddress = s
        return self

    def getLocalAddress(self):
        return self._localAddress

    def clone(self, localAddress=None):
        return self.__class__(self).setLocalAddress(
            localAddress is None and self.getLocalAddress() or localAddress
        )


class AbstractTransport:
    protoTransportDispatcher = None
    addressType = AbstractTransportAddress
    _cbFun = None

    @classmethod
    def isCompatibleWithDispatcher(
        cls, transportDispatcher: "AbstractTransportDispatcher"
    ):
        if cls.protoTransportDispatcher is None:
            raise error.CarrierError(
                f"Protocol transport dispatcher not specified for {cls}"
            )
        return isinstance(transportDispatcher, cls.protoTransportDispatcher)

    def registerCbFun(self, cbFun):
        if self._cbFun:
            raise error.CarrierError(
                f"Callback function {self._cbFun} already registered at {self}"
            )
        self._cbFun = cbFun

    def unregisterCbFun(self):
        self._cbFun = None

    def closeTransport(self):
        self.unregisterCbFun()

    # Public API

    def openClientMode(self, iface=None):
        raise error.CarrierError("Method not implemented")

    def openServerMode(self, iface):
        raise error.CarrierError("Method not implemented")

    def sendMessage(self, outgoingMessage, transportAddress: AbstractTransportAddress):
        raise error.CarrierError("Method not implemented")


class AbstractTransportDispatcher:
    __transports: "dict[tuple[int, ...], AbstractTransport]"
    __transportDomainMap: "dict[AbstractTransport, tuple[int, ...]]"
    __recvCallables: "dict['tuple[int, ...] | None', Callable]"
    __timerCallables: "list[TimerCallable]"
    __ticks: int
    __timerResolution: float
    __timerDelta: float
    __nextTime: float
    __routingCbFun: "Callable[[tuple[int, ...], AbstractTransportAddress, Any], 'tuple[int, ...]'] | None"  # fix message type

    def __init__(self):
        self.__transports = {}
        self.__transportDomainMap = {}
        self.__jobs = {}
        self.__recvCallables = {}
        self.__timerCallables = []
        self.__ticks = 0
        self.__timerResolution = 0.1
        self.__timerDelta = self.__timerResolution * 0.05
        self.__nextTime = 0
        self.__routingCbFun = None

    def _cbFun(
        self,
        incomingTransport: AbstractTransport,
        transportAddress: AbstractTransportAddress,
        incomingMessage,
    ):
        if incomingTransport in self.__transportDomainMap:
            transportDomain = self.__transportDomainMap[incomingTransport]

        else:
            raise error.CarrierError(f"Unregistered transport {incomingTransport}")

        if self.__routingCbFun:
            recvId = self.__routingCbFun(
                transportDomain, transportAddress, incomingMessage
            )

        else:
            recvId = None

        if recvId in self.__recvCallables:
            self.__recvCallables[recvId](
                self, transportDomain, transportAddress, incomingMessage
            )

        else:
            raise error.CarrierError(
                f'No callback for "{recvId!r}" found - loosing incoming event'
            )

    # Dispatcher API

    def registerRoutingCbFun(
        self,
        routingCbFun: "Callable[[tuple[int, ...], AbstractTransportAddress, Any], 'tuple[int, ...]'] | None",
    ):
        if self.__routingCbFun:
            raise error.CarrierError("Data routing callback already registered")
        self.__routingCbFun = routingCbFun

    def unregisterRoutingCbFun(self):
        if self.__routingCbFun:
            self.__routingCbFun = None

    def registerRecvCbFun(self, recvCb, recvId: "tuple[int, ...] | None" = None):
        if recvId in self.__recvCallables:
            raise error.CarrierError(
                "Receive callback {!r} already registered".format(
                    recvId is None and "<default>" or recvId
                )
            )

        self.__recvCallables[recvId] = recvCb

    def unregisterRecvCbFun(self, recvId: "tuple[int, ...] | None" = None):
        if recvId in self.__recvCallables:
            del self.__recvCallables[recvId]

    def registerTimerCbFun(
        self, timerCbFun: Callable, tickInterval: "float | None" = None
    ):
        if not tickInterval:
            tickInterval = self.__timerResolution

        self.__timerCallables.append(TimerCallable(timerCbFun, tickInterval))

    def unregisterTimerCbFun(self, timerCbFun: "TimerCallable | None" = None):
        if timerCbFun:
            self.__timerCallables.remove(timerCbFun)

        else:
            self.__timerCallables = []

    def registerTransport(
        self, transportDomain: "tuple[int, ...]", transport: AbstractTransport
    ):
        if transportDomain in self.__transports:
            raise error.CarrierError(f"Transport {transportDomain} already registered")
        transport.registerCbFun(self._cbFun)

        self.__transports[transportDomain] = transport
        self.__transportDomainMap[transport] = transportDomain

    def unregisterTransport(self, tDomain: "tuple[int, ...]"):
        if tDomain not in self.__transports:
            raise error.CarrierError(f"Transport {tDomain} not registered")
        self.__transports[tDomain].unregisterCbFun()
        del self.__transportDomainMap[self.__transports[tDomain]]
        del self.__transports[tDomain]

    def getTransport(self, transportDomain: "tuple[int, ...]"):
        if transportDomain in self.__transports:
            return self.__transports[transportDomain]
        raise error.CarrierError(f"Transport {transportDomain} not registered")

    def sendMessage(
        self,
        outgoingMessage,
        transportDomain: "tuple[int, ...]",
        transportAddress: AbstractTransportAddress,
    ):
        if transportDomain in self.__transports:
            self.__transports[transportDomain].sendMessage(
                outgoingMessage, transportAddress
            )

        else:
            raise error.CarrierError(
                f"No suitable transport domain for {transportDomain}"
            )

    def getTimerResolution(self):
        return self.__timerResolution

    def setTimerResolution(self, timerResolution: float):
        if timerResolution < 0.01 or timerResolution > 10:
            raise error.CarrierError("Impossible timer resolution")

        for timerCallable in self.__timerCallables:
            if timerCallable.interval == self.__timerResolution:
                # Update periodics for default resolutions
                timerCallable.interval = timerResolution

        self.__timerResolution = timerResolution
        self.__timerDelta = timerResolution * 0.05

    def getTimerTicks(self):
        return self.__ticks

    def handleTimerTick(self, timeNow: float):
        if self.__nextTime == 0:  # initial initialization
            self.__nextTime = timeNow + self.__timerResolution - self.__timerDelta

        if self.__nextTime >= timeNow:
            return

        self.__ticks += 1
        self.__nextTime = timeNow + self.__timerResolution - self.__timerDelta

        for timerCallable in self.__timerCallables:
            timerCallable(timeNow)

    def jobStarted(self, jobId, count: int = 1):
        if jobId in self.__jobs:
            self.__jobs[jobId] += count

        else:
            self.__jobs[jobId] = count

    def jobFinished(self, jobId, count: int = 1):
        self.__jobs[jobId] -= count
        if self.__jobs[jobId] == 0:
            del self.__jobs[jobId]

    def jobsArePending(self):
        return bool(self.__jobs)

    def runDispatcher(self, timeout: float = 0.0):
        raise error.CarrierError("Method not implemented")

    def closeDispatcher(self):
        for tDomain in list(self.__transports):
            self.__transports[tDomain].closeTransport()
            self.unregisterTransport(tDomain)

        self.__transports.clear()
        self.unregisterRecvCbFun()
        self.unregisterTimerCbFun()


class AbstractTransportAddress:
    _localAddress = None

    def setLocalAddress(self, s):
        self._localAddress = s
        return self

    def getLocalAddress(self):
        return self._localAddress

    def clone(self, localAddress=None):
        return self.__class__(self).setLocalAddress(
            localAddress is None and self.getLocalAddress() or localAddress
        )


class AbstractTransport:
    protoTransportDispatcher = None
    addressType = AbstractTransportAddress
    _cbFun = None

    @classmethod
    def isCompatibleWithDispatcher(cls, transportDispatcher):
        return isinstance(transportDispatcher, cls.protoTransportDispatcher)

    def registerCbFun(self, cbFun):
        if self._cbFun:
            raise error.CarrierError(
                f"Callback function {self._cbFun} already registered at {self}"
            )
        self._cbFun = cbFun

    def unregisterCbFun(self):
        self._cbFun = None

    def closeTransport(self):
        self.unregisterCbFun()

    # Public API

    def openClientMode(self, iface=None):
        raise error.CarrierError("Method not implemented")

    def openServerMode(self, iface):
        raise error.CarrierError("Method not implemented")

    def sendMessage(self, outgoingMessage, transportAddress):
        raise error.CarrierError("Method not implemented")
