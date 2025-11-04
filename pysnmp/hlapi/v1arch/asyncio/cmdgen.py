#
# This file is part of pysnmp software.
#
# Copyright (c) 2005-2020, Ilya Etingof <etingof@gmail.com>
# License: https://www.pysnmp.com/pysnmp/license.html
#
import asyncio
import warnings
from typing import AsyncGenerator

from pysnmp.hlapi import varbinds
from pysnmp.hlapi.transport import AbstractTransportTarget
from pysnmp.hlapi.v1arch.asyncio.auth import CommunityData
from pysnmp.hlapi.v1arch.asyncio.dispatch import SnmpDispatcher
from pysnmp.proto import api, errind
from pysnmp.proto.rfc1902 import Integer32, Null
from pysnmp.proto.rfc1905 import EndOfMibView, endOfMibView
from pysnmp.smi.rfc1902 import ObjectType, ObjectIdentity


__all__ = [
    "get_cmd",
    "next_cmd",
    "set_cmd",
    "bulk_cmd",
    "walk_cmd",
    "bulk_walk_cmd",
    "is_end_of_mib",
]

VB_PROCESSOR = varbinds.CommandGeneratorVarBinds()
is_end_of_mib = varbinds.is_end_of_mib


async def get_cmd(
    snmpDispatcher: SnmpDispatcher,
    authData: CommunityData,
    transportTarget: AbstractTransportTarget,
    *varBinds: ObjectType,
    **options,
) -> "tuple[errind.ErrorIndication | None, Integer32 | str | int | None, Integer32 | int | None, tuple[ObjectType, ...]]":
    r"""Creates a generator to perform SNMP GET query.

    When iterator gets advanced by :py:mod:`asyncio` main loop,
    SNMP GET request is sent (:RFC:`1905#section-4.2.1`).
    The iterator yields :py:class:`asyncio.Future` which gets done whenever
    response arrives or error occurs.

    Parameters
    ----------
    snmpDispatcher: :py:class:`~pysnmp.hlapi.v1arch.asyncio.SnmpDispatcher`
        Class instance representing asynio-based asynchronous event loop and
        associated state information.

    authData: :py:class:`~pysnmp.hlapi.v1arch.asyncio.CommunityData`
        Class instance representing SNMPv1/v2c credentials.

    transportTarget: :py:class:`~pysnmp.hlapi.v1arch.asyncio.UdpTransportTarget` or
        :py:class:`~pysnmp.hlapi.v1arch.asyncio.Udp6TransportTarget` Class instance representing
        transport type along with SNMP peer address.

    \*varBinds: :class:`tuple` of OID-value pairs or :py:class:`~pysnmp.smi.rfc1902.ObjectType`
        One or more class instances representing MIB variables to place
        into SNMP request.

    Note
    ----
    The `SnmpDispatcher` object may be expensive to create, therefore it is
    advised to maintain it for the lifecycle of the application/thread for
    as long as possible.

    Other Parameters
    ----------------
    \*\*options :
        Request options:

        * `lookupMib` - load MIB and resolve response MIB variables at
          the cost of slightly reduced performance. Default is `False`,
          unless :py:class:`~pysnmp.smi.rfc1902.ObjectType` is present
          among `varBinds` in which case `lookupMib` gets automatically
          enabled.

    Yields
    ------
    errorIndication: str
        True value indicates SNMP engine error.
    errorStatus: str
        True value indicates SNMP PDU error.
    errorIndex: int
        Non-zero value refers to `varBinds[errorIndex-1]`
    varBinds: tuple
        A sequence of OID-value pairs in form of base SNMP types (if
        `lookupMib` is `False`) or :py:class:`~pysnmp.smi.rfc1902.ObjectType`
        class instances (if `lookupMib` is `True`) representing MIB variables
        returned in SNMP response.

    Raises
    ------
    PySnmpError
        Or its derivative indicating that an error occurred while
        performing SNMP operation.

    Examples
    --------
    >>> import asyncio
    >>> from pysnmp.hlapi.v1arch.asyncio import *
    >>>
    >>> async def run():
    ...     errorIndication, errorStatus, errorIndex, varBinds = await get_cmd(
    ...         SnmpDispatcher(),
    ...         CommunityData('public'),
    ...         await UdpTransportTarget.create(('demo.pysnmp.com', 161)),
    ...         ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0))
    ...     )
    ...     print(errorIndication, errorStatus, errorIndex, varBinds)
    >>>
    >>> asyncio.run(run())
    (None, 0, 0, [ObjectType(ObjectIdentity(ObjectName('1.3.6.1.2.1.1.1.0')), DisplayString('SunOS zeus.pysnmp.com 4.1.3_U1 1 sun4m'))])
    >>>
    """

    def __callback(snmpDispatcher, stateHandle, errorIndication, rspPdu, cbCtx):
        lookupMib, future = cbCtx
        if future.cancelled():
            return

        if isinstance(errorIndication, errind.RequestTimedOut):
            future.set_result((errorIndication, 0, 0, ()))
            return

        errorStatus = pMod.apiPDU.get_error_status(rspPdu)
        errorIndex = pMod.apiPDU.get_error_index(rspPdu)

        varBinds = pMod.apiPDU.get_varbinds(rspPdu)

        try:
            varBindsUnmade = VB_PROCESSOR.unmake_varbinds(
                snmpDispatcher.cache, varBinds, lookupMib
            )
        except Exception as e:
            future.set_exception(e)
        else:
            future.set_result((
                errorIndication,
                errorStatus,
                errorIndex,
                varBindsUnmade,
            ))

    lookupMib = options.get("lookupMib")

    if not lookupMib and any(isinstance(x, ObjectType) for x in varBinds):
        lookupMib = True

    if lookupMib:
        varBinds = VB_PROCESSOR.make_varbinds(snmpDispatcher.cache, varBinds)

    pMod = api.PROTOCOL_MODULES[authData.mpModel]

    reqPdu = pMod.GetRequestPDU()
    pMod.apiPDU.set_defaults(reqPdu)
    pMod.apiPDU.set_varbinds(reqPdu, varBinds)

    future = asyncio.Future()

    snmpDispatcher.send_pdu(
        authData, transportTarget, reqPdu, cbFun=__callback, cbCtx=(lookupMib, future)
    )

    return await future


async def set_cmd(
    snmpDispatcher: SnmpDispatcher,
    authData: CommunityData,
    transportTarget: AbstractTransportTarget,
    *varBinds: ObjectType,
    **options,
) -> "tuple[errind.ErrorIndication | None, Integer32 | str | int | None, Integer32 | int | None, tuple[ObjectType, ...]]":
    r"""Creates a generator to perform SNMP SET query.

    When iterator gets advanced by :py:mod:`asyncio` main loop,
    SNMP SET request is sent (:RFC:`1905#section-4.2.5`).
    The iterator yields :py:class:`asyncio.Future` which gets done whenever
    response arrives or error occurs.

    Parameters
    ----------
    snmpDispatcher: :py:class:`~pysnmp.hlapi.v1arch.asyncio.SnmpDispatcher`
        Class instance representing asynio-based asynchronous event loop and
        associated state information.

    authData: :py:class:`~pysnmp.hlapi.v1arch.asyncio.CommunityData`
        Class instance representing SNMPv1/v2c credentials.

    transportTarget: :py:class:`~pysnmp.hlapi.v1arch.asyncio.UdpTransportTarget` or
        :py:class:`~pysnmp.hlapi.v1arch.asyncio.Udp6TransportTarget` Class instance representing
        transport type along with SNMP peer address.

    \*varBinds: :class:`tuple` of OID-value pairs or :py:class:`~pysnmp.smi.rfc1902.ObjectType`
        One or more class instances representing MIB variables to place
        into SNMP request.

    Note
    ----
    The `SnmpDispatcher` object may be expensive to create, therefore it is
    advised to maintain it for the lifecycle of the application/thread for
    as long as possible.

    Other Parameters
    ----------------
    \*\*options :
        Request options:

        * `lookupMib` - load MIB and resolve response MIB variables at
          the cost of slightly reduced performance. Default is `False`,
          unless :py:class:`~pysnmp.smi.rfc1902.ObjectType` is present
          among `varBinds` in which case `lookupMib` gets automatically
          enabled.

    Yields
    ------
    errorIndication: str
        True value indicates SNMP engine error.
    errorStatus: str
        True value indicates SNMP PDU error.
    errorIndex: int
        Non-zero value refers to `varBinds[errorIndex-1]`
    varBinds: tuple
        A sequence of OID-value pairs in form of base SNMP types (if
        `lookupMib` is `False`) or :py:class:`~pysnmp.smi.rfc1902.ObjectType`
        class instances (if `lookupMib` is `True`) representing MIB variables
        returned in SNMP response.

    Raises
    ------
    PySnmpError
        Or its derivative indicating that an error occurred while
        performing SNMP operation.

    Examples
    --------
    >>> import asyncio
    >>> from pysnmp.hlapi.v1arch.asyncio import *
    >>>
    >>> async def run():
    ...     errorIndication, errorStatus, errorIndex, varBinds = await set_cmd(
    ...         SnmpDispatcher(),
    ...         CommunityData('public'),
    ...         await UdpTransportTarget.create(('demo.pysnmp.com', 161)),
    ...         ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0), 'Linux i386')
    ...     )
    ...     print(errorIndication, errorStatus, errorIndex, varBinds)
    >>>
    >>> asyncio.run(run())
    (None, 0, 0, [ObjectType(ObjectIdentity(ObjectName('1.3.6.1.2.1.1.1.0')), DisplayString('Linux i386'))])
    >>>
    """

    def __callback(snmpDispatcher, stateHandle, errorIndication, rspPdu, cbCtx):
        lookupMib, future = cbCtx
        if future.cancelled():
            return

        errorStatus = pMod.apiPDU.get_error_status(rspPdu)
        errorIndex = pMod.apiPDU.get_error_index(rspPdu)

        varBinds = pMod.apiPDU.get_varbinds(rspPdu)

        try:
            varBindsUnmade = VB_PROCESSOR.unmake_varbinds(
                snmpDispatcher.cache, varBinds, lookupMib
            )
        except Exception as e:
            future.set_exception(e)
        else:
            future.set_result((
                errorIndication,
                errorStatus,
                errorIndex,
                varBindsUnmade,
            ))

    lookupMib = options.get("lookupMib")

    if not lookupMib and any(isinstance(x, ObjectType) for x in varBinds):
        lookupMib = True

    if lookupMib:
        varBinds = VB_PROCESSOR.make_varbinds(snmpDispatcher.cache, varBinds)

    pMod = api.PROTOCOL_MODULES[authData.mpModel]

    reqPdu = pMod.SetRequestPDU()
    pMod.apiPDU.set_defaults(reqPdu)
    pMod.apiPDU.set_varbinds(reqPdu, varBinds)

    future = asyncio.Future()

    snmpDispatcher.send_pdu(
        authData, transportTarget, reqPdu, cbFun=__callback, cbCtx=(lookupMib, future)
    )

    return await future


async def next_cmd(
    snmpDispatcher: SnmpDispatcher,
    authData: CommunityData,
    transportTarget: AbstractTransportTarget,
    *varBinds: ObjectType,
    **options,
) -> "tuple[errind.ErrorIndication | None, Integer32 | str | int | None, Integer32 | int | None, tuple[ObjectType, ...]]":
    r"""Creates a generator to perform SNMP GETNEXT query.

    When iterator gets advanced by :py:mod:`asyncio` main loop,
    SNMP GETNEXT request is send (:RFC:`1905#section-4.2.2`).
    The iterator yields :py:class:`asyncio.Future` which gets done whenever
    response arrives or error occurs.

    Parameters
    ----------
    snmpDispatcher: :py:class:`~pysnmp.hlapi.v1arch.asyncio.SnmpDispatcher`
        Class instance representing asynio-based asynchronous event loop and
        associated state information.

    authData: :py:class:`~pysnmp.hlapi.v1arch.asyncio.CommunityData`
        Class instance representing SNMPv1/v2c credentials.

    transportTarget: :py:class:`~pysnmp.hlapi.v1arch.asyncio.UdpTransportTarget` or
        :py:class:`~pysnmp.hlapi.v1arch.asyncio.Udp6TransportTarget` Class instance representing
        transport type along with SNMP peer address.

    \*varBinds: :class:`tuple` of OID-value pairs or :py:class:`~pysnmp.smi.rfc1902.ObjectType`
        One or more class instances representing MIB variables to place
        into SNMP request.

    Note
    ----
    The `SnmpDispatcher` object may be expensive to create, therefore it is
    advised to maintain it for the lifecycle of the application/thread for
    as long as possible.

    Other Parameters
    ----------------
    \*\*options:
        Request options:

        * `lookupMib` - load MIB and resolve response MIB variables at
          the cost of slightly reduced performance. Default is `False`,
          unless :py:class:`~pysnmp.smi.rfc1902.ObjectType` is present
          among `varBinds` in which case `lookupMib` gets automatically
          enabled.

    Yields
    ------
    errorIndication: str
        True value indicates SNMP engine error.
    errorStatus: str
        True value indicates SNMP PDU error.
    errorIndex: int
        Non-zero value refers to `varBinds[errorIndex-1]`
    varBinds: tuple
        A sequence of sequences (e.g. 2-D array) of OID-value pairs in form
        of base SNMP types (if `lookupMib` is `False`) or
        :py:class:`~pysnmp.smi.rfc1902.ObjectType` class instances (if
        `lookupMib` is `True`) a table of MIB variables returned in SNMP
        response. Inner sequences represent table rows and ordered exactly
        the same as `varBinds` in request. Response to GETNEXT always contain
        a single row.

    Raises
    ------
    PySnmpError
        Or its derivative indicating that an error occurred while
        performing SNMP operation.

    Examples
    --------
    >>> import asyncio
    >>> from pysnmp.hlapi.v1arch.asyncio import *
    >>>
    >>> async def run():
    ...     errorIndication, errorStatus, errorIndex, varBinds = await next_cmd(
    ...         SnmpDispatcher(),
    ...         CommunityData('public'),
    ...         await UdpTransportTarget.create(('demo.pysnmp.com', 161)),
    ...         ObjectType(ObjectIdentity('SNMPv2-MIB', 'system'))
    ...     )
    ...     print(errorIndication, errorStatus, errorIndex, varBinds)
    >>>
    >>> asyncio.run(run())
    (None, 0, 0, [[ObjectType(ObjectIdentity('1.3.6.1.2.1.1.1.0'), DisplayString('Linux i386'))]])
    >>>
    """

    def __callback(
        snmpDispatcher: SnmpDispatcher,
        stateHandle,
        errorIndication: errind.ErrorIndication,
        rspPdu,
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
            errorIndication = None  # type: ignore # TODO: fix this

        errorStatus = pMod.apiPDU.get_error_status(rspPdu)
        errorIndex = pMod.apiPDU.get_error_index(rspPdu)

        varBinds = pMod.apiPDU.get_varbinds(rspPdu)

        try:
            varBindsUnmade = VB_PROCESSOR.unmake_varbinds(
                snmpDispatcher.cache, varBinds, lookupMib
            )
        except Exception as e:
            future.set_exception(e)
        else:
            future.set_result((
                errorIndication,
                errorStatus,
                errorIndex,
                varBindsUnmade,
            ))

    lookupMib = options.get("lookupMib")

    if not lookupMib and any(isinstance(x, ObjectType) for x in varBinds):
        lookupMib = True

    if lookupMib:
        varBinds = VB_PROCESSOR.make_varbinds(snmpDispatcher.cache, varBinds)

    pMod = api.PROTOCOL_MODULES[authData.mpModel]

    reqPdu = pMod.GetNextRequestPDU()
    pMod.apiPDU.set_defaults(reqPdu)
    pMod.apiPDU.set_varbinds(reqPdu, varBinds)

    future = asyncio.Future()

    snmpDispatcher.send_pdu(
        authData, transportTarget, reqPdu, cbFun=__callback, cbCtx=(lookupMib, future)
    )

    return await future


async def bulk_cmd(
    snmpDispatcher: SnmpDispatcher,
    authData: CommunityData,
    transportTarget: AbstractTransportTarget,
    nonRepeaters: int,
    maxRepetitions: int,
    *varBinds: ObjectType,
    **options,
) -> "tuple[errind.ErrorIndication | None, Integer32 | str | int | None, Integer32 | int | None, tuple[ObjectType, ...]]":
    r"""Creates a generator to perform SNMP GETBULK query.

    When iterator gets advanced by :py:mod:`asyncio` main loop,
    SNMP GETBULK request is send (:RFC:`1905#section-4.2.3`).
    The iterator yields :py:class:`asyncio.Future` which gets done whenever
    response arrives or error occurs.

    Parameters
    ----------
    snmpDispatcher: :py:class:`~pysnmp.hlapi.v1arch.asyncio.SnmpDispatcher`
        Class instance representing asynio-based asynchronous event loop and
        associated state information.

    authData: :py:class:`~pysnmp.hlapi.v1arch.asyncio.CommunityData`
        Class instance representing SNMPv2c credentials. (SNMPv1 / mpModel=0 is not allowed)

    transportTarget: :py:class:`~pysnmp.hlapi.v1arch.asyncio.UdpTransportTarget` or
        :py:class:`~pysnmp.hlapi.v1arch.asyncio.Udp6TransportTarget` Class instance representing
        transport type along with SNMP peer address.

    nonRepeaters : int
        One MIB variable is requested in response for the first
        `nonRepeaters` MIB variables in request.

    maxRepetitions : int
        `maxRepetitions` MIB variables are requested in response for each
        of the remaining MIB variables in the request (e.g. excluding
        `nonRepeaters`). Remote SNMP engine may choose lesser value than
        requested.

    \*varBinds: :class:`tuple` of OID-value pairs or :py:class:`~pysnmp.smi.rfc1902.ObjectType`
        One or more class instances representing MIB variables to place
        into SNMP request.

    Other Parameters
    ----------------
    \*\*options :
        Request options:

        * `lookupMib` - load MIB and resolve response MIB variables at
          the cost of slightly reduced performance. Default is `False`,
          unless :py:class:`~pysnmp.smi.rfc1902.ObjectType` is present
          among `varBinds` in which case `lookupMib` gets automatically
          enabled.

    Yields
    ------
    errorIndication: str
        True value indicates SNMP engine error.
    errorStatus: str
        True value indicates SNMP PDU error.
    errorIndex: int
        Non-zero value refers to `varBinds[errorIndex-1]`
    varBindTable: tuple
        A flat sequence of variables returned in the SNMP GETBULK
        response. If ``lookupMib`` is ``True``, elements are
        :py:class:`~pysnmp.smi.rfc1902.ObjectType` instances; otherwise
        they are OID-value pairs of base types. The order is the raw
        wire order: first the non-repeaters (at most one each), then up
        to ``maxRepetitions`` groups of the repeaters in request order.

        The maximum length is
        ``nonRepeaters + maxRepetitions * (len(varBinds) - nonRepeaters)``,
        but the agent may return fewer items (e.g., due to
        :py:obj:`~pysnmp.proto.rfc1905.endOfMibView` or truncation).

        See :rfc:`3416#section-4.2.3` for details on the underlying
        ``GetBulkRequest-PDU`` and the associated ``GetResponse-PDU``.

    Raises
    ------
    PySnmpError
        Or its derivative indicating that an error occurred while
        performing SNMP operation.

    Examples
    --------
    >>> import asyncio
    >>> from pysnmp.hlapi.v1arch.asyncio import *
    >>>
    >>> async def run():
    ...     errorIndication, errorStatus, errorIndex, varBinds = await bulk_cmd(
    ...         SnmpDispatcher(),
    ...         CommunityData('public'),
    ...         await UdpTransportTarget.create(('demo.pysnmp.com', 161)),
    ...         0, 2,
    ...         ObjectType(ObjectIdentity('SNMPv2-MIB', 'system'))
    ...     )
    ...     print(errorIndication, errorStatus, errorIndex, varBinds)
    >>>
    >>> asyncio.run(run())
    (None, 0, 0, [ObjectType(ObjectIdentity(ObjectName('1.3.6.1.2.1.1.1.0')), DisplayString('SunOS zeus.pysnmp.com 4.1.3_U1 1 sun4m')), ObjectType(ObjectIdentity(ObjectName('1.3.6.1.2.1.1.2.0')), ObjectIdentifier('1.3.6.1.4.1.424242.1.1'))])
    >>>
    """

    def __callback(
        snmpDispatcher: SnmpDispatcher,
        stateHandle,
        errorIndication: errind.ErrorIndication,
        rspPdu,
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
            errorIndication = None  # type: ignore # TODO: fix here

        errorStatus = pMod.apiPDU.get_error_status(rspPdu)
        errorIndex = pMod.apiPDU.get_error_index(rspPdu)

        varBinds = pMod.apiBulkPDU.get_varbinds(rspPdu)

        try:
            varBindsUnmade = VB_PROCESSOR.unmake_varbinds(
                snmpDispatcher.cache, varBinds, lookupMib
            )
        except Exception as e:
            future.set_exception(e)
        else:
            future.set_result((
                errorIndication,
                errorStatus,
                errorIndex,
                varBindsUnmade,
            ))

    lookupMib = options.get("lookupMib")

    if not lookupMib and any(isinstance(x, ObjectType) for x in varBinds):
        lookupMib = True

    if lookupMib:
        varBinds = VB_PROCESSOR.make_varbinds(snmpDispatcher.cache, varBinds)

    pMod = api.PROTOCOL_MODULES[authData.mpModel]

    reqPdu = pMod.GetBulkRequestPDU()
    pMod.apiPDU.set_defaults(reqPdu)
    pMod.apiBulkPDU.set_non_repeaters(reqPdu, nonRepeaters)
    pMod.apiBulkPDU.set_max_repetitions(reqPdu, maxRepetitions)
    pMod.apiPDU.set_varbinds(reqPdu, varBinds)

    future = asyncio.Future()

    snmpDispatcher.send_pdu(
        authData, transportTarget, reqPdu, cbFun=__callback, cbCtx=(lookupMib, future)
    )

    return await future


async def walk_cmd(
    dispatcher: SnmpDispatcher,
    authData: CommunityData,
    transportTarget: AbstractTransportTarget,
    varBind: ObjectType,
    **options,
) -> AsyncGenerator[
    "tuple[errind.ErrorIndication | None, Integer32 | str | int | None, Integer32 | int | None, tuple[ObjectType, ...]]",
    None,
]:
    r"""Creates a generator to perform one or more SNMP GETNEXT queries.

    On each iteration, new SNMP GETNEXT request is send
    (:RFC:`1905#section-4.2.2`). The iterator blocks waiting for response
    to arrive or error to occur.

    Parameters
    ----------
    snmpEngine : :py:class:`~pysnmp.hlapi.v1arch.asyncio.SnmpDispatcher`
        Class instance representing SNMP engine.

    authData : :py:class:`~pysnmp.hlapi.v1arch.asyncio.CommunityData`
        Class instance representing SNMP credentials.

    transportTarget : :py:class:`~pysnmp.hlapi.v1arch.asyncio.UdpTransportTarget` or :py:class:`~pysnmp.hlapi.v1arch.asyncio.Udp6TransportTarget`
        Class instance representing transport type along with SNMP peer address.

    varBind : :py:class:`~pysnmp.smi.rfc1902.ObjectType`
        One class instance representing MIB variables to place
        into SNMP request.

    Other Parameters
    ----------------
    \*\*options :
        Request options:

            * `lookupMib` - load MIB and resolve response MIB variables at
              the cost of slightly reduced performance. Default is `True`.
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
    The `walk_cmd` generator will be exhausted on any of the following
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
    >>> from pysnmp.hlapi.v1arch.asyncio import *
    >>> objects = walk_cmd(SnmpEngine(),
    ...             CommunityData('public'),
    ...             await UdpTransportTarget.create(('demo.pysnmp.com', 161)),
    ...             ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr')))
    ... g = [item async for item in objects]
    >>> next(g)
    (None, 0, 0, [ObjectType(ObjectIdentity(ObjectName('1.3.6.1.2.1.1.1.0')), DisplayString('SunOS zeus.pysnmp.com 4.1.3_U1 1 sun4m'))])
    >>> g.send( [ ObjectType(ObjectIdentity('IF-MIB', 'ifInOctets')) ] )
    (None, 0, 0, [(ObjectName('1.3.6.1.2.1.2.2.1.10.1'), Counter32(284817787))])
    """
    lexicographicMode = options.get("lexicographicMode", True)
    ignoreNonIncreasingOid = options.get("ignoreNonIncreasingOid", False)
    maxRows = options.get("maxRows", 0)
    maxCalls = options.get("maxCalls", 0)

    initialVars = [
        x[0] for x in VB_PROCESSOR.make_varbinds(dispatcher.cache, (varBind,))
    ]

    totalRows = totalCalls = 0

    while True:
        if varBind:
            errorIndication, errorStatus, errorIndex, varBindTable = await next_cmd(
                dispatcher,
                authData,
                transportTarget,
                (varBind[0], Null("")),  # type: ignore
                **dict(lookupMib=options.get("lookupMib", True)),
            )
            if (
                ignoreNonIncreasingOid
                and errorIndication
                and isinstance(errorIndication, errind.OidNotIncreasing)
            ):
                errorIndication = None

            if errorIndication:
                yield (errorIndication, errorStatus, errorIndex, (varBind,))
                return
            elif errorStatus:
                if errorStatus == 2:
                    # Hide SNMPv1 noSuchName error which leaks in here
                    # from SNMPv1 Agent through internal pysnmp proxy.
                    errorStatus = 0
                    errorIndex = 0
                return
            else:
                stopFlag = True

                varBind = varBindTable[0]

                name, val = varBind
                foundEnding = isinstance(val, Null) or isinstance(val, EndOfMibView)
                foundBeyond = not lexicographicMode and not initialVars[0].isPrefixOf(
                    name
                )
                if foundEnding or foundBeyond:
                    return

                if stopFlag and varBind[1] is not endOfMibView:
                    stopFlag = False

                if stopFlag:
                    return

                totalRows += 1
                totalCalls += 1
        else:
            errorIndication = errorStatus = errorIndex = None
            varBind = None  # type: ignore

        initialVarBinds: "tuple[ObjectType, ...]|None" = yield (
            errorIndication,
            errorStatus,
            errorIndex,
            (varBind,),
        )

        if initialVarBinds:
            varBind = initialVarBinds[0]
            initialVars = [
                x[0]
                for x in VB_PROCESSOR.make_varbinds(dispatcher.cache, initialVarBinds)
            ]

        if maxRows and totalRows >= maxRows:
            return

        if maxCalls and totalCalls >= maxCalls:
            return


async def bulk_walk_cmd(
    dispatcher: SnmpDispatcher,
    authData: CommunityData,
    transportTarget: AbstractTransportTarget,
    nonRepeaters: int,
    maxRepetitions: int,
    varBind: ObjectType,
    **options,
) -> AsyncGenerator[
    "tuple[errind.ErrorIndication | None, Integer32 | str | int | None, Integer32 | int | None, tuple[ObjectType, ...]]",
    None,
]:
    r"""Creates a generator to perform one or more SNMP GETBULK queries.

    On each iteration, new SNMP GETBULK request is send
    (:RFC:`1905#section-4.2.3`). The iterator blocks waiting for response
    to arrive or error to occur.

    Parameters
    ----------
    snmpEngine : :py:class:`~pysnmp.hlapi.v1arch.asyncio.SnmpDispatcher`
        Class instance representing SNMP engine.

    authData : :py:class:`~pysnmp.hlapi.v1arch.asyncio.CommunityData`
        Class instance representing SNMPv2c credentials. (SNMPv1 / mpModel=0 is not allowed)

    transportTarget : :py:class:`~pysnmp.hlapi.v1arch.asyncio.UdpTransportTarget` or :py:class:`~pysnmp.hlapi.v1arch.asyncio.Udp6TransportTarget`
        Class instance representing transport type along with SNMP peer address.

    nonRepeaters : int
        One MIB variable is requested in response for the first
        `nonRepeaters` MIB variables in request.

    maxRepetitions : int
        `maxRepetitions` MIB variables are requested in response for each
        of the remaining MIB variables in the request (e.g. excluding
        `nonRepeaters`). Remote SNMP engine may choose lesser value than
        requested.

    varBind : :py:class:`~pysnmp.smi.rfc1902.ObjectType`
        One class instance representing MIB variables to place
        into SNMP request.

    Other Parameters
    ----------------
    \*\*options :
        Request options:

            * `lookupMib` - load MIB and resolve response MIB variables at
              the cost of slightly reduced performance. Default is `True`.
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
    The `bulk_walk_cmd` generator will be exhausted on any of the following
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
    >>> from pysnmp.hlapi.v1arch.asyncio import *
    >>> objects = bulk_walk_cmd(SnmpEngine(),
    ...             CommunityData('public'),
    ...             await UdpTransportTarget.create(('demo.pysnmp.com', 161)),
    ...             0, 25,
    ...             ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr')))
    ... g = [item async for item in objects]
    >>> next(g)
    (None, 0, 0, [ObjectType(ObjectIdentity(ObjectName('1.3.6.1.2.1.1.1.0')), DisplayString('SunOS zeus.pysnmp.com 4.1.3_U1 1 sun4m'))])
    >>> g.send( [ ObjectType(ObjectIdentity('IF-MIB', 'ifInOctets')) ] )
    (None, 0, 0, [(ObjectName('1.3.6.1.2.1.2.2.1.10.1'), Counter32(284817787))])
    """
    lexicographicMode = options.get("lexicographicMode", True)
    ignoreNonIncreasingOid = options.get("ignoreNonIncreasingOid", False)
    maxRows = options.get("maxRows", 0)
    maxCalls = options.get("maxCalls", 0)

    initialVars = [
        x[0] for x in VB_PROCESSOR.make_varbinds(dispatcher.cache, (varBind,))
    ]

    totalRows = totalCalls = 0

    varBinds: "tuple[ObjectType, ...]" = (varBind,)

    while True:
        if maxRows and totalRows < maxRows:
            maxRepetitions = min(maxRepetitions, maxRows - totalRows)

        if varBinds:
            # Create a simple tuple with the OID from the previous response and Null value
            # This approach matches walk_cmd() and works with both lookupMib=True and False
            nextVarBinds = [(varBinds[-1][0], Null(""))]

            errorIndication, errorStatus, errorIndex, varBindTable = await bulk_cmd(
                dispatcher,
                authData,
                transportTarget,
                nonRepeaters,
                maxRepetitions,
                *nextVarBinds,
                **dict(lookupMib=options.get("lookupMib", True)),
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
                    varBindTable and varBinds,
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
                    varBinds,
                )
                return
            else:
                stopFlag = True
                varBinds = varBindTable

                for col, varBind in enumerate(varBinds):
                    name, val = varBind
                    foundEnding = isinstance(val, Null) or isinstance(val, EndOfMibView)
                    foundBeyond = not lexicographicMode and not initialVars[
                        0
                    ].isPrefixOf(name)
                    if foundEnding or foundBeyond:
                        stopFlag = True
                        result = varBinds[:col]
                        if len(result) > 0:
                            yield (
                                errorIndication,
                                errorStatus,
                                errorIndex,
                                result,
                            )
                        return

                    if stopFlag and varBinds[col][1] is not endOfMibView:
                        stopFlag = False

                if stopFlag:
                    return

                totalRows += 1
                totalCalls += 1
        else:
            errorIndication = errorStatus = errorIndex = None
            varBinds = ()

        initialVarBinds: "tuple[ObjectType, ...]|None" = yield (
            errorIndication,
            errorStatus,
            errorIndex,
            varBinds,
        )
        if initialVarBinds:
            varBinds = initialVarBinds
            initialVars = [
                x[0] for x in VB_PROCESSOR.make_varbinds(dispatcher.cache, varBinds)
            ]

        if maxRows and totalRows >= maxRows:
            return

        if maxCalls and totalCalls >= maxCalls:
            return


async def multi_bulk_walk_cmd(
    dispatcher: SnmpDispatcher,
    authData: CommunityData,
    transportTarget: AbstractTransportTarget,
    nonRepeaters: int,
    maxRepetitions: int,
    *varBinds: ObjectType,
    **options,
) -> AsyncGenerator[
    "tuple[errind.ErrorIndication | None, Integer32 | str | int | None, Integer32 | int | None, tuple[ObjectType, ...]]",
    None,
]:
    r"""Creates a generator to perform SNMP GETBULK queries with multiple OID trees.

    This function extends the bulk_walk_cmd functionality to support walking multiple
    OID trees simultaneously while respecting lexicographic mode for each varbind
    independently. Each varbind is tracked separately and will stop iteration when
    it reaches its natural boundary or goes out of scope.

    On each iteration, new SNMP GETBULK request is sent (:RFC:`1905#section-4.2.3`).
    The iterator blocks waiting for response to arrive or error to occur. Unlike
    bulk_walk_cmd which only handles a single varbind, this function can handle
    multiple varbinds in parallel, applying lexicographic mode filtering to each.

    Parameters
    ----------
    snmpEngine : :py:class:`~pysnmp.hlapi.v1arch.asyncio.SnmpDispatcher`
        Class instance representing SNMP engine.

    authData : :py:class:`~pysnmp.hlapi.v1arch.asyncio.CommunityData`
        Class instance representing SNMPv2c credentials. (SNMPv1 / mpModel=0 is not allowed)

    transportTarget : :py:class:`~pysnmp.hlapi.v1arch.asyncio.UdpTransportTarget` or :py:class:`~pysnmp.hlapi.v1arch.asyncio.Udp6TransportTarget`
        Class instance representing transport type along with SNMP peer address.

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
        into SNMP request. Each varbind represents a separate OID tree to walk.

    Other Parameters
    ----------------
    \*\*options :
        Request options:

            * `lookupMib` - load MIB and resolve response MIB variables at
              the cost of slightly reduced performance. Default is `True`.
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
        Non-zero value refers to varBinds[errorIndex-1]
    varBinds : tuple
        A sequence of :py:class:`~pysnmp.smi.rfc1902.ObjectType` class
        instances representing MIB variables returned in SNMP response.
        Contains all valid OIDs from the current GETBULK response batch.

    Raises
    ------
    PySnmpError
        Or its derivative indicating that an error occurred while
        performing SNMP operation.

    Notes
    -----
    Key Behavioral Differences from bulk_walk_cmd:

     - Supports multiple varbinds simultaneously: the generator can walk multiple
      OID subtrees in parallel within a single SNMP session.
     - Each varbind is independently tracked: completion, last OID, and
      lexicographic boundaries are maintained per varbind.
     - lexicographicMode is applied per-varbind: a varbind stops only when its
      own scope is exhausted if lexicographicMode=False. Other varbinds continue.
     - Can optionally ignore non-increasing OIDs: if ignoreNonIncreasingOid=True,
      the generator continues even when the agent returns OIDs that are not
      greater than previous ones.
     - Returns all valid responses from each GETBULK call in a single yield: all
      active varbinds' results are grouped together in the same batch.
     - Respects maxRows and maxCalls limits across all varbinds combined.
     - Handles timeouts gracefully: the generator continues unless the error
      is non-recoverable.

    """
    lexicographicMode = options.get("lexicographicMode", True)
    ignoreNonIncreasingOid = options.get("ignoreNonIncreasingOid", False)
    maxRows = options.get("maxRows", 0)
    maxCalls = options.get("maxCalls", 0)

    initialVars = [x[0] for x in VB_PROCESSOR.make_varbinds(dispatcher.cache, varBinds)]
    num_varbinds = len(initialVars)

    # Track state for each varbind independently
    completed = [False] * num_varbinds

    # Track last seen OID per varbind (used for next bulk_cmd request)
    last_oids = [
        vb[0] if isinstance(vb[0], ObjectIdentity) else ObjectIdentity(vb[0])
        for vb in varBinds
    ]

    totalRows = 0
    totalCalls = 0

    # Continue until all varbinds are exhausted
    while True:

        valid_results = []
        if varBinds:
            # Adjust maxRepetitions if approaching maxRows limit
            if maxRows and totalRows < maxRows:
                adjusted_max_reps = min(maxRepetitions, maxRows - totalRows)
            else:
                adjusted_max_reps = maxRepetitions

            # Build request varbinds from currently active (non-completed) varbinds
            active_indices = [i for i in range(num_varbinds) if not completed[i]]

            if not active_indices:
                # All varbinds have completed their walk
                return

            # Create request varbinds using last known OIDs for active varbinds
            request_varbinds = [
                ObjectType(
                    (
                        last_oids[i]
                        if isinstance(last_oids[i], ObjectIdentity)
                        else ObjectIdentity(last_oids[i])
                    ),
                    Null(""),
                )
                for i in active_indices
            ]

            errorIndication, errorStatus, errorIndex, varBindTable = await bulk_cmd(
                dispatcher,
                authData,
                transportTarget,
                nonRepeaters,
                adjusted_max_reps,
                *request_varbinds,
                **dict(lookupMib=options.get("lookupMib", True)),
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
                    varBindTable and tuple(varBindTable) or (),
                )
                if errorIndication != errind.requestTimedOut:
                    return
            elif errorStatus:
                # SNMP PDU errors from agent
                if errorStatus == 2:
                    # Hide SNMPv1 noSuchName error which leaks in here
                    # from SNMPv1 Agent through internal pysnmp proxy
                    errorStatus = 0
                    errorIndex = 0

                yield (
                    errorIndication,
                    errorStatus,
                    errorIndex,
                    tuple(ObjectType(last_oids[i], Null("")) for i in active_indices),
                )
                return
            else:
                # Successful response - process the varBindTable
                if not varBindTable:
                    return

                # Group responses by source varbind
                # bulk_cmd returns: [vb0_r0, vb1_r0, ..., vbN_r0, vb0_r1, vb1_r1, ...]
                # Which regroup to: [[vb0_r0, vb0_r1, ...], [vb1_r0, vb1_r1, ...]]
                num_active = len(active_indices)
                responses_per_varbind = [[] for _ in range(num_active)]

                for idx, response_vb in enumerate(varBindTable):
                    active_vb_idx = idx % num_active
                    responses_per_varbind[active_vb_idx].append(response_vb)

                # Collect all valid responses from this bulk_cmd call
                stopFlag = True

                for active_idx, original_idx in enumerate(active_indices):
                    responses = responses_per_varbind[active_idx]

                    if not responses:
                        completed[original_idx] = True
                        continue

                    # Track last valid OID for this varbind
                    last_valid_oid = None
                    varbind_still_active = False

                    # Process all responses for this varbind
                    for response_vb in responses:
                        name, val = response_vb
                        foundEnding = isinstance(val, Null) or isinstance(
                            val, EndOfMibView
                        )

                        # Check if beyond initial scope (when lexicographicMode=False)
                        foundBeyond = not lexicographicMode and not initialVars[
                            original_idx
                        ].isPrefixOf(name)

                        # Check for endOfMibView sentinel
                        is_end_of_mib_val = val is endOfMibView

                        if foundEnding or foundBeyond or is_end_of_mib_val:
                            # This response is beyond scope or end - mark varbind as completed and stop processing
                            completed[original_idx] = True
                            break

                        # Valid response - add to results
                        valid_results.append(response_vb)
                        last_valid_oid = name
                        varbind_still_active = True
                        stopFlag = False

                    # Update last OID for next iteration if we have valid responses
                    if last_valid_oid is not None and varbind_still_active:
                        last_oids[original_idx] = last_valid_oid

                totalRows += len(valid_results)
                totalCalls += 1

                # If stopFlag is True, all varbinds have completed
                if stopFlag:
                    # Check if we have any final results to yield
                    if valid_results:
                        yield (
                            errorIndication,
                            errorStatus,
                            errorIndex,
                            tuple(valid_results),
                        )
                    return

                # If no valid results, stop walking
                if not valid_results:
                    return

        else:
            errorIndication = errorStatus = errorIndex = None
            varBinds = ()

        # Yield all collected valid varBinds for this batch
        initialVarBinds: "tuple[ObjectType, ...]|None" = (
            yield errorIndication,
            errorStatus,
            errorIndex,
            tuple(valid_results),
        )

        if initialVarBinds:
            num_new = len(initialVarBinds)

            new_initial_vars = [
                x[0]
                for x in VB_PROCESSOR.make_varbinds(dispatcher.cache, initialVarBinds)
            ]

            initialVars = new_initial_vars
            num_varbinds = num_new
            completed = [False] * num_varbinds
            last_oids = [vb[0] for vb in initialVarBinds]

        if maxRows and totalRows >= maxRows:
            return

        if maxCalls and totalCalls >= maxCalls:
            return

        if all(completed):
            return


# Compatibility API
deprecated_attributes = {
    "getCmd": "get_cmd",
    "setCmd": "set_cmd",
    "nextCmd": "next_cmd",
    "bulkCmd": "bulk_cmd",
    "walkCmd": "walk_cmd",
    "bulkWalkCmd": "bulk_walk_cmd",
    "isEndOfMib": "is_end_of_mib",
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
