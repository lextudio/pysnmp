#
# This file is part of pysnmp software.
#
# Copyright (c) 2005-2020, Ilya Etingof <etingof@gmail.com>
# License: https://www.pysnmp.com/pysnmp/license.html
#
# Copyright (C) 2014, Zebra Technologies
# Authors: Matt Hooks <me@matthooks.com>
#          Zachary Lorusso <zlorusso@gmail.com>
# Modified by Ilya Etingof <ilya@snmplabs.com>
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
# IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGE.
#
import asyncio


from pysnmp.entity.engine import SnmpEngine
from pysnmp.hlapi.transport import AbstractTransportTarget
from pysnmp.hlapi.v3arch.auth import *
from pysnmp.hlapi.v3arch.context import *
from pysnmp.hlapi.v3arch.lcd import *
from pysnmp.hlapi.varbinds import *
from pysnmp.hlapi.v3arch.asyncio.transport import *
from pysnmp.entity.rfc3413 import cmdgen
from pysnmp.proto import errind
from pysnmp.proto.api import v2c
from pysnmp.smi.rfc1902 import *

__all__ = ["getCmd", "nextCmd", "setCmd", "bulkCmd", "isEndOfMib"]

VB_PROCESSOR = CommandGeneratorVarBinds()
LCD = CommandGeneratorLcdConfigurator()

isEndOfMib = lambda varBinds: not v2c.apiPDU.getNextVarBinds(varBinds)[1]


async def getCmd(
    snmpEngine: SnmpEngine,
    authData: "CommunityData | UsmUserData",
    transportTarget: AbstractTransportTarget,
    contextData: ContextData,
    *varBinds,
    **options
) -> "tuple[errind.ErrorIndication, int, int, tuple[ObjectType]]":
    r"""Creates a generator to perform SNMP GET query.

    When iterator gets advanced by :py:mod:`asyncio` main loop,
    SNMP GET request is send (:RFC:`1905#section-4.2.1`).
    The iterator yields :py:class:`asyncio.get_running_loop().create_future()` which gets done whenever
    response arrives or error occurs.

    Parameters
    ----------
    snmpEngine : :py:class:`~pysnmp.hlapi.SnmpEngine`
        Class instance representing SNMP engine.

    authData : :py:class:`~pysnmp.hlapi.CommunityData` or :py:class:`~pysnmp.hlapi.UsmUserData`
        Class instance representing SNMP credentials.

    transportTarget : :py:class:`~pysnmp.hlapi.asyncio.UdpTransportTarget` or :py:class:`~pysnmp.hlapi.asyncio.Udp6TransportTarget`
        Class instance representing transport type along with SNMP peer address.

    contextData : :py:class:`~pysnmp.hlapi.ContextData`
        Class instance representing SNMP ContextEngineId and ContextName values.

    *varBinds : :py:class:`~pysnmp.smi.rfc1902.ObjectType`
        One or more class instances representing MIB variables to place
        into SNMP request.

    Other Parameters
    ----------------
    **options :
        Request options:

            * `lookupMib` - load MIB and resolve response MIB variables at
              the cost of slightly reduced performance. Default is `True`.

    Yields
    ------
    errorIndication : :py:class:`~pysnmp.proto.errind.ErrorIndication`
        True value indicates SNMP engine error.
    errorStatus : str
        True value indicates SNMP PDU error.
    errorIndex : int
        Non-zero value refers to `varBinds[errorIndex-1]`
    varBinds : tuple
        A sequence of :py:class:`~pysnmp.smi.rfc1902.ObjectType` class
        instances representing MIB variables returned in SNMP response.

    Raises
    ------
    PySnmpError
        Or its derivative indicating that an error occurred while
        performing SNMP operation.

    Examples
    --------
    >>> import asyncio
    >>> from pysnmp.hlapi.asyncio import *
    >>>
    >>> async def run():
    ...     errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
    ...         SnmpEngine(),
    ...         CommunityData('public'),
    ...         UdpTransportTarget(('demo.pysnmp.com', 161)),
    ...         ContextData(),
    ...         ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0))
    ...     )
    ...     print(errorIndication, errorStatus, errorIndex, varBinds)
    >>>
    >>> asyncio.run(run())
    (None, 0, 0, [ObjectType(ObjectIdentity(ObjectName('1.3.6.1.2.1.1.1.0')), DisplayString('SunOS zeus.pysnmp.com 4.1.3_U1 1 sun4m'))])
    >>>

    """

    def __cbFun(
        snmpEngine,
        sendRequestHandle,
        errorIndication,
        errorStatus,
        errorIndex,
        varBinds,
        cbCtx,
    ):
        lookupMib, future = cbCtx

        if future.cancelled():
            return

        try:
            varBindsUnmade = VB_PROCESSOR.unmakeVarBinds(
                snmpEngine.cache, varBinds, lookupMib
            )

        except Exception as e:
            future.set_exception(e)

        else:
            future.set_result(
                (errorIndication, errorStatus, errorIndex, varBindsUnmade)
            )

    addrName, paramsName = LCD.configure(
        snmpEngine, authData, transportTarget, contextData.contextName
    )

    future = asyncio.get_running_loop().create_future()

    cmdgen.GetCommandGenerator().sendVarBinds(
        snmpEngine,
        addrName,
        contextData.contextEngineId,
        contextData.contextName,
        VB_PROCESSOR.makeVarBinds(snmpEngine.cache, varBinds),
        __cbFun,
        (options.get("lookupMib", True), future),
    )
    return await future


async def setCmd(
    snmpEngine: SnmpEngine,
    authData: "CommunityData | UsmUserData",
    transportTarget: AbstractTransportTarget,
    contextData: ContextData,
    *varBinds,
    **options
) -> "tuple[errind.ErrorIndication, int, int, tuple[ObjectType]]":
    r"""Creates a generator to perform SNMP SET query.

    When iterator gets advanced by :py:mod:`asyncio` main loop,
    SNMP SET request is send (:RFC:`1905#section-4.2.5`).
    The iterator yields :py:class:`asyncio.get_running_loop().create_future()` which gets done whenever
    response arrives or error occurs.

    Parameters
    ----------
    snmpEngine : :py:class:`~pysnmp.hlapi.SnmpEngine`
        Class instance representing SNMP engine.

    authData : :py:class:`~pysnmp.hlapi.CommunityData` or :py:class:`~pysnmp.hlapi.UsmUserData`
        Class instance representing SNMP credentials.

    transportTarget : :py:class:`~pysnmp.hlapi.asyncio.UdpTransportTarget` or :py:class:`~pysnmp.hlapi.asyncio.Udp6TransportTarget`
        Class instance representing transport type along with SNMP peer address.

    contextData : :py:class:`~pysnmp.hlapi.ContextData`
        Class instance representing SNMP ContextEngineId and ContextName values.

    *varBinds : :py:class:`~pysnmp.smi.rfc1902.ObjectType`
        One or more class instances representing MIB variables to place
        into SNMP request.

    Other Parameters
    ----------------
    **options :
        Request options:

            * `lookupMib` - load MIB and resolve response MIB variables at
              the cost of slightly reduced performance. Default is `True`.

    Yields
    ------
    errorIndication : :py:class:`~pysnmp.proto.errind.ErrorIndication`
        True value indicates SNMP engine error.
    errorStatus : str
        True value indicates SNMP PDU error.
    errorIndex : int
        Non-zero value refers to `varBinds[errorIndex-1]`
    varBinds : tuple
        A sequence of :py:class:`~pysnmp.smi.rfc1902.ObjectType` class
        instances representing MIB variables returned in SNMP response.

    Raises
    ------
    PySnmpError
        Or its derivative indicating that an error occurred while
        performing SNMP operation.

    Examples
    --------
    >>> import asyncio
    >>> from pysnmp.hlapi.asyncio import *
    >>>
    >>> async def run():
    ...     errorIndication, errorStatus, errorIndex, varBinds = await setCmd(
    ...         SnmpEngine(),
    ...         CommunityData('public'),
    ...         UdpTransportTarget(('demo.pysnmp.com', 161)),
    ...         ContextData(),
    ...         ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0), 'Linux i386')
    ...     )
    ...     print(errorIndication, errorStatus, errorIndex, varBinds)
    >>>
    >>> asyncio.run(run())
    (None, 0, 0, [ObjectType(ObjectIdentity(ObjectName('1.3.6.1.2.1.1.1.0')), DisplayString('Linux i386'))])
    >>>

    """

    def __cbFun(
        snmpEngine,
        sendRequestHandle,
        errorIndication,
        errorStatus,
        errorIndex,
        varBinds,
        cbCtx,
    ):
        lookupMib, future = cbCtx

        if future.cancelled():
            return

        try:
            varBindsUnmade = VB_PROCESSOR.unmakeVarBinds(
                snmpEngine.cache, varBinds, lookupMib
            )

        except Exception as e:
            future.set_exception(e)

        else:
            future.set_result(
                (errorIndication, errorStatus, errorIndex, varBindsUnmade)
            )

    addrName, paramsName = LCD.configure(
        snmpEngine, authData, transportTarget, contextData.contextName
    )

    future = asyncio.get_running_loop().create_future()

    cmdgen.SetCommandGenerator().sendVarBinds(
        snmpEngine,
        addrName,
        contextData.contextEngineId,
        contextData.contextName,
        VB_PROCESSOR.makeVarBinds(snmpEngine.cache, varBinds),
        __cbFun,
        (options.get("lookupMib", True), future),
    )
    return await future


async def nextCmd(
    snmpEngine: SnmpEngine,
    authData: "CommunityData | UsmUserData",
    transportTarget: AbstractTransportTarget,
    contextData: ContextData,
    *varBinds,
    **options
) -> "tuple[errind.ErrorIndication, int, int, tuple[ObjectType]]":
    r"""Creates a generator to perform SNMP GETNEXT query.

    When iterator gets advanced by :py:mod:`asyncio` main loop,
    SNMP GETNEXT request is send (:RFC:`1905#section-4.2.2`).
    The iterator yields :py:class:`asyncio.get_running_loop().create_future()` which gets done whenever
    response arrives or error occurs.

    Parameters
    ----------
    snmpEngine : :py:class:`~pysnmp.hlapi.SnmpEngine`
        Class instance representing SNMP engine.

    authData : :py:class:`~pysnmp.hlapi.CommunityData` or :py:class:`~pysnmp.hlapi.UsmUserData`
        Class instance representing SNMP credentials.

    transportTarget : :py:class:`~pysnmp.hlapi.asyncio.UdpTransportTarget` or :py:class:`~pysnmp.hlapi.asyncio.Udp6TransportTarget`
        Class instance representing transport type along with SNMP peer address.

    contextData : :py:class:`~pysnmp.hlapi.ContextData`
        Class instance representing SNMP ContextEngineId and ContextName values.

    *varBinds : :py:class:`~pysnmp.smi.rfc1902.ObjectType`
        One or more class instances representing MIB variables to place
        into SNMP request.

    Other Parameters
    ----------------
    **options :
        Request options:

            * `lookupMib` - load MIB and resolve response MIB variables at
              the cost of slightly reduced performance. Default is `True`.

    Yields
    ------
    errorIndication : :py:class:`~pysnmp.proto.errind.ErrorIndication`
        True value indicates SNMP engine error.
    errorStatus : str
        True value indicates SNMP PDU error.
    errorIndex : int
        Non-zero value refers to `varBinds[errorIndex-1]`
    varBinds : tuple
        A sequence of sequences (e.g. 2-D array) of
        :py:class:`~pysnmp.smi.rfc1902.ObjectType` class instances
        representing a table of MIB variables returned in SNMP response.
        Inner sequences represent table rows and ordered exactly the same
        as `varBinds` in request. Response to GETNEXT always contain
        a single row.

    Raises
    ------
    PySnmpError
        Or its derivative indicating that an error occurred while
        performing SNMP operation.

    Examples
    --------
    >>> import asyncio
    >>> from pysnmp.hlapi.asyncio import *
    >>>
    >>> async def run():
    ...     errorIndication, errorStatus, errorIndex, varBinds = await nextCmd(
    ...         SnmpEngine(),
    ...         CommunityData('public'),
    ...         UdpTransportTarget(('demo.pysnmp.com', 161)),
    ...         ContextData(),
    ...         ObjectType(ObjectIdentity('SNMPv2-MIB', 'system'))
    ...     )
    ...     print(errorIndication, errorStatus, errorIndex, varBinds)
    >>>
    >>> asyncio.run(run())
    (None, 0, 0, [[ObjectType(ObjectIdentity('1.3.6.1.2.1.1.1.0'), DisplayString('Linux i386'))]])
    >>>

    """

    def __cbFun(
        snmpEngine,
        sendRequestHandle,
        errorIndication,
        errorStatus,
        errorIndex,
        varBindTable,
        cbCtx,
    ):
        lookupMib, future = cbCtx
        if future.cancelled():
            return

        try:
            varBindsUnmade = [
                VB_PROCESSOR.unmakeVarBinds(
                    snmpEngine.cache, varBindTableRow, lookupMib
                )
                for varBindTableRow in varBindTable
            ]

        except Exception as e:
            future.set_exception(e)

        else:
            future.set_result(
                (errorIndication, errorStatus, errorIndex, varBindsUnmade)
            )

    addrName, paramsName = LCD.configure(
        snmpEngine, authData, transportTarget, contextData.contextName
    )

    future = asyncio.get_running_loop().create_future()

    cmdgen.NextCommandGenerator().sendVarBinds(
        snmpEngine,
        addrName,
        contextData.contextEngineId,
        contextData.contextName,
        VB_PROCESSOR.makeVarBinds(snmpEngine.cache, varBinds),
        __cbFun,
        (options.get("lookupMib", True), future),
    )
    return await future


async def bulkCmd(
    snmpEngine,
    authData,
    transportTarget,
    contextData,
    nonRepeaters,
    maxRepetitions,
    *varBinds,
    **options
) -> "tuple[errind.ErrorIndication, int, int, tuple[ObjectType]]":
    r"""Creates a generator to perform SNMP GETBULK query.

    When iterator gets advanced by :py:mod:`asyncio` main loop,
    SNMP GETBULK request is send (:RFC:`1905#section-4.2.3`).
    The iterator yields :py:class:`asyncio.get_running_loop().create_future()` which gets done whenever
    response arrives or error occurs.

    Parameters
    ----------
    snmpEngine : :py:class:`~pysnmp.hlapi.SnmpEngine`
        Class instance representing SNMP engine.

    authData : :py:class:`~pysnmp.hlapi.CommunityData` or :py:class:`~pysnmp.hlapi.UsmUserData`
        Class instance representing SNMP credentials.

    transportTarget : :py:class:`~pysnmp.hlapi.asyncio.UdpTransportTarget` or :py:class:`~pysnmp.hlapi.asyncio.Udp6TransportTarget`
        Class instance representing transport type along with SNMP peer address.

    contextData : :py:class:`~pysnmp.hlapi.ContextData`
        Class instance representing SNMP ContextEngineId and ContextName values.

    nonRepeaters : int
        One MIB variable is requested in response for the first
        `nonRepeaters` MIB variables in request.

    maxRepetitions : int
        `maxRepetitions` MIB variables are requested in response for each
        of the remaining MIB variables in the request (e.g. excluding
        `nonRepeaters`). Remote SNMP engine may choose lesser value than
        requested.

    *varBinds : :py:class:`~pysnmp.smi.rfc1902.ObjectType`
        One or more class instances representing MIB variables to place
        into SNMP request.

    Other Parameters
    ----------------
    **options :
        Request options:

            * `lookupMib` - load MIB and resolve response MIB variables at
              the cost of slightly reduced performance. Default is `True`.

    Yields
    ------
    errorIndication : :py:class:`~pysnmp.proto.errind.ErrorIndication`
        True value indicates SNMP engine error.
    errorStatus : str
        True value indicates SNMP PDU error.
    errorIndex : int
        Non-zero value refers to `varBinds[errorIndex-1]`
    varBindTable : tuple
        A sequence of sequences (e.g. 2-D array) of
        :py:class:`~pysnmp.smi.rfc1902.ObjectType` class instances
        representing a table of MIB variables returned in SNMP response, with
        up to ``maxRepetitions`` rows, i.e.
        ``len(varBindTable) <= maxRepetitions``.

        For ``0 <= i < len(varBindTable)`` and ``0 <= j < len(varBinds)``,
        ``varBindTable[i][j]`` represents:

        - For non-repeaters (``j < nonRepeaters``), the first lexicographic
          successor of ``varBinds[j]``, regardless the value of ``i``, or an
          :py:class:`~pysnmp.smi.rfc1902.ObjectType` instance with the
          :py:obj:`~pysnmp.proto.rfc1905.endOfMibView` value if no such
          successor exists;
        - For repeaters (``j >= nonRepeaters``), the ``i``-th lexicographic
          successor of ``varBinds[j]``, or an
          :py:class:`~pysnmp.smi.rfc1902.ObjectType` instance with the
          :py:obj:`~pysnmp.proto.rfc1905.endOfMibView` value if no such
          successor exists.

        See :rfc:`3416#section-4.2.3` for details on the underlying
        ``GetBulkRequest-PDU`` and the associated ``GetResponse-PDU``, such as
        specific conditions under which the server may truncate the response,
        causing ``varBindTable`` to have less than ``maxRepetitions`` rows.

    Raises
    ------
    PySnmpError
        Or its derivative indicating that an error occurred while
        performing SNMP operation.

    Examples
    --------
    >>> import asyncio
    >>> from pysnmp.hlapi.asyncio import *
    >>>
    >>> async def run():
    ...     errorIndication, errorStatus, errorIndex, varBinds = await bulkCmd(
    ...         SnmpEngine(),
    ...         CommunityData('public'),
    ...         UdpTransportTarget(('demo.pysnmp.com', 161)),
    ...         ContextData(),
    ...         0, 2,
    ...         ObjectType(ObjectIdentity('SNMPv2-MIB', 'system'))
    ...     )
    ...     print(errorIndication, errorStatus, errorIndex, varBinds)
    >>>
    >>> asyncio.get_event_loop().run_until_complete(run())
    (None, 0, 0, [[ObjectType(ObjectIdentity(ObjectName('1.3.6.1.2.1.1.1.0')), DisplayString('SunOS zeus.pysnmp.com 4.1.3_U1 1 sun4m'))], [ObjectType(ObjectIdentity(ObjectName('1.3.6.1.2.1.1.2.0')), ObjectIdentifier('1.3.6.1.4.1.424242.1.1'))]])
    >>>

    """

    def __cbFun(
        snmpEngine,
        sendRequestHandle,
        errorIndication,
        errorStatus,
        errorIndex,
        varBindTable,
        cbCtx,
    ):
        lookupMib, future = cbCtx

        if future.cancelled():
            return

        try:
            varBindsUnmade = [
                VB_PROCESSOR.unmakeVarBinds(
                    snmpEngine.cache, varBindTableRow, lookupMib
                )
                for varBindTableRow in varBindTable
            ]

        except Exception as e:
            future.set_exception(e)

        else:
            future.set_result(
                (errorIndication, errorStatus, errorIndex, varBindsUnmade)
            )

    addrName, paramsName = LCD.configure(
        snmpEngine, authData, transportTarget, contextData.contextName
    )

    future = asyncio.get_running_loop().create_future()

    cmdgen.BulkCommandGenerator().sendVarBinds(
        snmpEngine,
        addrName,
        contextData.contextEngineId,
        contextData.contextName,
        nonRepeaters,
        maxRepetitions,
        VB_PROCESSOR.makeVarBinds(snmpEngine.cache, varBinds),
        __cbFun,
        (options.get("lookupMib", True), future),
    )
    return await future
