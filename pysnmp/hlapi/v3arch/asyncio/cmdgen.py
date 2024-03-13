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
import sys
from typing import AsyncGenerator, Generator
from pysnmp.entity.engine import SnmpEngine
from pysnmp.hlapi.transport import AbstractTransportTarget
from pysnmp.proto.api import v2c
from pysnmp.proto.rfc1905 import EndOfMibView, endOfMibView

from pysnmp.smi.rfc1902 import *
from pysnmp.hlapi.v3arch.auth import *
from pysnmp.hlapi.v3arch.context import *
from pysnmp.hlapi.v3arch.lcd import *
from pysnmp.hlapi.varbinds import *
from pysnmp.hlapi.v3arch.asyncio.transport import *
from pysnmp.entity.rfc3413 import cmdgen
from pysnmp.proto.rfc1902 import Integer32, Null
from pysnmp.proto import errind

import asyncio


__all__ = [
    "getCmd",
    "nextCmd",
    "setCmd",
    "bulkCmd",
    "isEndOfMib",
    "walkCmd",
    "bulkWalkCmd",
]

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
) -> "tuple[errind.ErrorIndication, Integer32 | int, Integer32 | int, tuple[ObjectType]]":
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
        errorIndication: errind.ErrorIndication,
        errorStatus: "Integer32 | int",
        errorIndex: "Integer32 | int",
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
) -> "tuple[errind.ErrorIndication, Integer32 | int, Integer32 | int, tuple[ObjectType]]":
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
        errorIndication: errind.ErrorIndication,
        errorStatus: "Integer32 | int",
        errorIndex: "Integer32 | int",
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
) -> "tuple[errind.ErrorIndication, Integer32 | int, Integer32 | int, tuple[ObjectType]]":
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
        errorIndication: errind.ErrorIndication,
        errorStatus: "Integer32 | int",
        errorIndex: "Integer32 | int",
        varBindTable,
        cbCtx,
    ):
        lookupMib, future = cbCtx
        if future.cancelled():
            return
        if (
            options.get("ignoreNonIncreasingOid", False)
            and errorIndication
            and isinstance(errorIndication, errind.OidNotIncreasing)
        ):
            errorIndication = None  # TODO: fix this
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
) -> "tuple[errind.ErrorIndication, Integer32 | int, Integer32 | int, tuple[ObjectType]]":
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
        errorIndication: errind.ErrorIndication,
        errorStatus: "Integer32 | int",
        errorIndex: "Integer32 | int",
        varBindTable,
        cbCtx,
    ):
        lookupMib, future = cbCtx

        if future.cancelled():
            return
        if (
            options.get("ignoreNonIncreasingOid", False)
            and errorIndication
            and isinstance(errorIndication, errind.OidNotIncreasing)
        ):
            errorIndication = None  # TODO: fix here
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


async def walkCmd(
    snmpEngine: SnmpEngine,
    authData: "CommunityData | UsmUserData",
    transportTarget: AbstractTransportTarget,
    contextData: ContextData,
    *varBinds,
    **options
) -> AsyncGenerator[
    "tuple[errind.ErrorIndication, Integer32 | int, Integer32 | int, tuple[ObjectType]]",
    None,
]:
    r"""Creates a generator to perform one or more SNMP GETNEXT queries.

    On each iteration, new SNMP GETNEXT request is send
    (:RFC:`1905#section-4.2.2`). The iterator blocks waiting for response
    to arrive or error to occur.

    Parameters
    ----------
    snmpEngine : :py:class:`~pysnmp.hlapi.SnmpEngine`
        Class instance representing SNMP engine.

    authData : :py:class:`~pysnmp.hlapi.CommunityData` or :py:class:`~pysnmp.hlapi.UsmUserData`
        Class instance representing SNMP credentials.

    transportTarget : :py:class:`~pysnmp.hlapi.asyncore.UdpTransportTarget` or :py:class:`~pysnmp.hlapi.asyncore.Udp6TransportTarget`
        Class instance representing transport type along with SNMP peer address.

    contextData : :py:class:`~pysnmp.hlapi.ContextData`
        Class instance representing SNMP ContextEngineId and ContextName values.

    \*varBinds : :py:class:`~pysnmp.smi.rfc1902.ObjectType`
        One or more class instances representing MIB variables to place
        into SNMP request.

    Other Parameters
    ----------------
    \*\*options :
        Request options:

            * `lookupMib` - load MIB and resolve response MIB variables at
              the cost of slightly reduced performance. Default is `True`.
              Default is `True`.
            * `lexicographicMode` - walk SNMP agent's MIB till the end (if `True`),
              otherwise (if `False`) stop iteration when all response MIB
              variables leave the scope of initial MIB variables in
              `varBinds`. Default is `True`.
            * `ignoreNonIncreasingOid` - continue iteration even if response
              MIB variables (OIDs) are not greater then request MIB variables.
              Be aware that setting it to `True` may cause infinite loop between
              SNMP management and agent applications. Default is `False`.
            * `maxRows` - stop iteration once this generator instance processed
              `maxRows` of SNMP conceptual table. Default is `0` (no limit).
            * `maxCalls` - stop iteration once this generator instance processed
              `maxCalls` responses. Default is 0 (no limit).

    Yields
    ------
    errorIndication : str
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

    Notes
    -----
    The `nextCmd` generator will be exhausted on any of the following
    conditions:

    * SNMP engine error occurs thus `errorIndication` is `True`
    * SNMP PDU `errorStatus` is reported as `True`
    * SNMP :py:class:`~pysnmp.proto.rfc1905.EndOfMibView` values
      (also known as *SNMP exception values*) are reported for all
      MIB variables in `varBinds`
    * *lexicographicMode* option is `True` and SNMP agent reports
      end-of-mib or *lexicographicMode* is `False` and all
      response MIB variables leave the scope of `varBinds`

    At any moment a new sequence of `varBinds` could be send back into
    running generator (supported since Python 2.6).

    Examples
    --------
    >>> from pysnmp.hlapi import *
    >>> g = walkCmd(SnmpEngine(),
    ...             CommunityData('public'),
    ...             UdpTransportTarget(('demo.pysnmp.com', 161)),
    ...             ContextData(),
    ...             ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr')))
    >>> next(g)
    (None, 0, 0, [ObjectType(ObjectIdentity(ObjectName('1.3.6.1.2.1.1.1.0')), DisplayString('SunOS zeus.pysnmp.com 4.1.3_U1 1 sun4m'))])
    >>> g.send( [ ObjectType(ObjectIdentity('IF-MIB', 'ifInOctets')) ] )
    (None, 0, 0, [(ObjectName('1.3.6.1.2.1.2.2.1.10.1'), Counter32(284817787))])
    """

    lexicographicMode = options.get("lexicographicMode", True)
    ignoreNonIncreasingOid = options.get("ignoreNonIncreasingOid", False)
    maxRows = options.get("maxRows", 0)
    maxCalls = options.get("maxCalls", 0)

    vbProcessor = CommandGeneratorVarBinds()

    initialVars = [x[0] for x in vbProcessor.makeVarBinds(snmpEngine, varBinds)]

    totalRows = totalCalls = 0

    while True:
        previousVarBinds = varBinds
        if varBinds:
            errorIndication, errorStatus, errorIndex, varBindTable = await nextCmd(
                snmpEngine,
                authData,
                transportTarget,
                contextData,
                *[(x[0], Null("")) for x in varBinds],
                **dict(lookupMib=options.get("lookupMib", True))
            )
            if (
                ignoreNonIncreasingOid
                and errorIndication
                and isinstance(errorIndication, errind.OidNotIncreasing)
            ):
                errorIndication = None

            if errorIndication:
                yield (errorIndication, errorStatus, errorIndex, varBinds)
                return
            elif errorStatus:
                if errorStatus == 2:
                    # Hide SNMPv1 noSuchName error which leaks in here
                    # from SNMPv1 Agent through internal pysnmp proxy.
                    errorStatus = 0
                    errorIndex = 0
                yield (errorIndication, errorStatus, errorIndex, varBinds)
                return
            else:
                stopFlag = True

                varBinds = varBindTable[0]

                for col, varBind in enumerate(varBinds):
                    name, val = varBind
                    if isinstance(val, Null):
                        varBinds[col] = previousVarBinds[col][0], endOfMibView

                    if not lexicographicMode and not initialVars[col].isPrefixOf(name):
                        varBinds[col] = previousVarBinds[col][0], endOfMibView

                    if stopFlag and varBinds[col][1] is not endOfMibView:
                        stopFlag = False

                if stopFlag:
                    return

                totalRows += 1
                totalCalls += 1
        else:
            errorIndication = errorStatus = errorIndex = None
            varBinds = []

        initialVarBinds = (yield errorIndication, errorStatus, errorIndex, varBinds)

        if initialVarBinds:
            varBinds = initialVarBinds
            initialVars = [x[0] for x in vbProcessor.makeVarBinds(snmpEngine, varBinds)]

        if maxRows and totalRows >= maxRows:
            return

        if maxCalls and totalCalls >= maxCalls:
            return


async def bulkWalkCmd(
    snmpEngine: SnmpEngine,
    authData: "CommunityData | UsmUserData",
    transportTarget: AbstractTransportTarget,
    contextData: ContextData,
    nonRepeaters,
    maxRepetitions,
    *varBinds,
    **options
) -> AsyncGenerator[
    "tuple[errind.ErrorIndication, Integer32 | int, Integer32 | int, tuple[ObjectType]]",
    None,
]:
    r"""Creates a generator to perform one or more SNMP GETBULK queries.

    On each iteration, new SNMP GETBULK request is send
    (:RFC:`1905#section-4.2.3`). The iterator blocks waiting for response
    to arrive or error to occur.

    Parameters
    ----------
    snmpEngine : :py:class:`~pysnmp.hlapi.SnmpEngine`
        Class instance representing SNMP engine.

    authData : :py:class:`~pysnmp.hlapi.CommunityData` or :py:class:`~pysnmp.hlapi.UsmUserData`
        Class instance representing SNMP credentials.

    transportTarget : :py:class:`~pysnmp.hlapi.asyncore.UdpTransportTarget` or :py:class:`~pysnmp.hlapi.asyncore.Udp6TransportTarget`
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

    \*varBinds : :py:class:`~pysnmp.smi.rfc1902.ObjectType`
        One or more class instances representing MIB variables to place
        into SNMP request.

    Other Parameters
    ----------------
    \*\*options :
        Request options:

            * `lookupMib` - load MIB and resolve response MIB variables at
              the cost of slightly reduced performance. Default is `True`.
              Default is `True`.
            * `lexicographicMode` - walk SNMP agent's MIB till the end (if `True`),
              otherwise (if `False`) stop iteration when all response MIB
              variables leave the scope of initial MIB variables in
              `varBinds`. Default is `True`.
            * `ignoreNonIncreasingOid` - continue iteration even if response
              MIB variables (OIDs) are not greater then request MIB variables.
              Be aware that setting it to `True` may cause infinite loop between
              SNMP management and agent applications. Default is `False`.
            * `maxRows` - stop iteration once this generator instance processed
              `maxRows` of SNMP conceptual table. Default is `0` (no limit).
            * `maxCalls` - stop iteration once this generator instance processed
              `maxCalls` responses. Default is 0 (no limit).

    Yields
    ------
    errorIndication : str
        True value indicates SNMP engine error.
    errorStatus : str
        True value indicates SNMP PDU error.
    errorIndex : int
        Non-zero value refers to \*varBinds[errorIndex-1]
    varBinds : tuple
        A sequence of :py:class:`~pysnmp.smi.rfc1902.ObjectType` class
        instances representing MIB variables returned in SNMP response.

    Raises
    ------
    PySnmpError
        Or its derivative indicating that an error occurred while
        performing SNMP operation.

    Notes
    -----
    The `bulkCmd` generator will be exhausted on any of the following
    conditions:

    * SNMP engine error occurs thus `errorIndication` is `True`
    * SNMP PDU `errorStatus` is reported as `True`
    * SNMP :py:class:`~pysnmp.proto.rfc1905.EndOfMibView` values
      (also known as *SNMP exception values*) are reported for all
      MIB variables in `varBinds`
    * *lexicographicMode* option is `True` and SNMP agent reports
      end-of-mib or *lexicographicMode* is `False` and all
      response MIB variables leave the scope of `varBinds`

    At any moment a new sequence of `varBinds` could be send back into
    running generator (supported since Python 2.6).

    Setting `maxRepetitions` value to 15..50 might significantly improve
    system performance, as many MIB variables get packed into a single
    response message at once.

    Examples
    --------
    >>> from pysnmp.hlapi import *
    >>> g = bulkWalkCmd(SnmpEngine(),
    ...             CommunityData('public'),
    ...             UdpTransportTarget(('demo.pysnmp.com', 161)),
    ...             ContextData(),
    ...             0, 25,
    ...             ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr')))
    >>> next(g)
    (None, 0, 0, [ObjectType(ObjectIdentity(ObjectName('1.3.6.1.2.1.1.1.0')), DisplayString('SunOS zeus.pysnmp.com 4.1.3_U1 1 sun4m'))])
    >>> g.send( [ ObjectType(ObjectIdentity('IF-MIB', 'ifInOctets')) ] )
    (None, 0, 0, [(ObjectName('1.3.6.1.2.1.2.2.1.10.1'), Counter32(284817787))])
    """

    lexicographicMode = options.get("lexicographicMode", True)
    ignoreNonIncreasingOid = options.get("ignoreNonIncreasingOid", False)
    maxRows = options.get("maxRows", 0)
    maxCalls = options.get("maxCalls", 0)

    vbProcessor = CommandGeneratorVarBinds()

    initialVars = [x[0] for x in vbProcessor.makeVarBinds(snmpEngine, varBinds)]
    nullVarBinds = [False] * len(initialVars)

    totalRows = totalCalls = 0
    stopFlag = False

    while not stopFlag:
        if maxRows and totalRows < maxRows:
            maxRepetitions = min(maxRepetitions, maxRows - totalRows)

        previousVarBinds = varBinds

        errorIndication, errorStatus, errorIndex, varBindTable = await bulkCmd(
            snmpEngine,
            authData,
            transportTarget,
            contextData,
            nonRepeaters,
            maxRepetitions,
            *[(x[0], Null("")) for x in varBinds],
            **dict(lookupMib=options.get("lookupMib", True))
        )

        if (
            ignoreNonIncreasingOid
            and errorIndication
            and isinstance(errorIndication, errind.OidNotIncreasing)
        ):
            errorIndication = None

        if errorIndication:
            yield (
                errorIndication,
                errorStatus,
                errorIndex,
                varBindTable and varBindTable[0] or [],
            )
            if errorIndication != errind.requestTimedOut:
                return
        elif errorStatus:
            if errorStatus == 2:
                # Hide SNMPv1 noSuchName error which leaks in here
                # from SNMPv1 Agent through internal pysnmp proxy.
                errorStatus = 0
                errorIndex = 0
            yield (
                errorIndication,
                errorStatus,
                errorIndex,
                varBindTable and varBindTable[0] or [],
            )
            return
        else:
            for row in range(len(varBindTable)):
                stopFlag = True
                if len(varBindTable[row]) != len(initialVars):
                    varBindTable = row and varBindTable[: row - 1] or []
                    break
                for col in range(len(varBindTable[row])):
                    name, val = varBindTable[row][col]
                    if row:
                        previousVarBinds = varBindTable[row - 1]
                    if nullVarBinds[col]:
                        varBindTable[row][col] = previousVarBinds[col][0], endOfMibView
                        continue
                    stopFlag = False
                    if isinstance(val, Null) or isinstance(val, EndOfMibView):
                        varBindTable[row][col] = previousVarBinds[col][0], endOfMibView
                        nullVarBinds[col] = True
                    if not lexicographicMode and not initialVars[col].isPrefixOf(name):
                        varBindTable[row][col] = previousVarBinds[col][0], endOfMibView
                        nullVarBinds[col] = True
                if stopFlag:
                    varBindTable = row and varBindTable[: row - 1] or []
                    break

            totalRows += len(varBindTable)
            totalCalls += 1

            if maxRows and totalRows >= maxRows:
                if totalRows > maxRows:
                    varBindTable = varBindTable[: -(totalRows - maxRows)]
                stopFlag = True

            if maxCalls and totalCalls >= maxCalls:
                stopFlag = True

            varBinds = varBindTable and varBindTable[-1] or []

            for varBindRow in varBindTable:
                initialVarBinds = (
                    yield errorIndication,
                    errorStatus,
                    errorIndex,
                    varBindRow,
                )

                if initialVarBinds:
                    varBinds = initialVarBinds
                    initialVars = [
                        x[0] for x in vbProcessor.makeVarBinds(snmpEngine, varBinds)
                    ]
                    nullVarBinds = [False] * len(initialVars)
