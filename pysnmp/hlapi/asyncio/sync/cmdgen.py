from pysnmp.entity.engine import SnmpEngine
from pysnmp.hlapi.v3arch.asyncio.cmdgen import (
    getCmd as _getCmd,
    setCmd as _setCmd,
    nextCmd as _nextCmd,
    bulkCmd as _bulkCmd,
)
from pysnmp.hlapi.v3arch.auth import CommunityData, UsmUserData
from pysnmp.hlapi.v3arch.context import ContextData
from pysnmp.hlapi.transport import AbstractTransportTarget
from pysnmp.hlapi.varbinds import *

import asyncio
from pysnmp.proto import errind

from pysnmp.proto.rfc1902 import Integer32
from pysnmp.smi.rfc1902 import ObjectType


__all__ = ["getCmd", "nextCmd", "setCmd", "bulkCmd"]


def getCmd(
    snmpEngine: SnmpEngine,
    authData: "CommunityData | UsmUserData",
    transportTarget: AbstractTransportTarget,
    contextData: ContextData,
    *varBinds,
    **options
) -> (
    "tuple[errind.ErrorIndication, Integer32 | int, Integer32 | int, tuple[ObjectType]]"
):
    r"""Creates a generator to perform one or more SNMP GET queries.

    On each iteration, new SNMP GET request is send (:RFC:`1905#section-4.2.1`).
    The iterator blocks waiting for response to arrive or error to occur.

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

    \*varBinds : :py:class:`~pysnmp.smi.rfc1902.ObjectType`
        One or more class instances representing MIB variables to place
        into SNMP request.

    Other Parameters
    ----------------
    \*\*options :
        Request options:

            * `lookupMib` - load MIB and resolve response MIB variables at
              the cost of slightly reduced performance. Default is `True`.

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
    The `getCmd` generator will be exhausted immediately unless
    a new sequence of `varBinds` are send back into running generator
    (supported since Python 2.6).

    Examples
    --------
    >>> from pysnmp.hlapi import *
    >>> g = getCmd(SnmpEngine(),
    ...            CommunityData('public'),
    ...            UdpTransportTarget(('demo.pysnmp.com', 161)),
    ...            ContextData(),
    ...            ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0)))
    >>> g
    (None, 0, 0, [ObjectType(ObjectIdentity(ObjectName('1.3.6.1.2.1.1.1.0')), DisplayString('SunOS zeus.pysnmp.com 4.1.3_U1 1 sun4m'))])
    >>>

    """

    loop = asyncio.get_event_loop()
    if loop.is_running():
        future = asyncio.ensure_future(
            _getCmd(
                snmpEngine, authData, transportTarget, contextData, *varBinds, **options
            )
        )
        return loop.run_until_complete(future)
    else:
        return loop.run_until_complete(
            _getCmd(
                snmpEngine, authData, transportTarget, contextData, *varBinds, **options
            )
        )


def setCmd(
    snmpEngine: SnmpEngine,
    authData: "CommunityData | UsmUserData",
    transportTarget: AbstractTransportTarget,
    contextData: ContextData,
    *varBinds,
    **options
) -> (
    "tuple[errind.ErrorIndication, Integer32 | int, Integer32 | int, tuple[ObjectType]]"
):
    r"""Creates a generator to perform one or more SNMP SET queries.

    On each iteration, new SNMP SET request is send (:RFC:`1905#section-4.2.5`).
    The iterator blocks waiting for response to arrive or error to occur.

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
    The `setCmd` generator will be exhausted immidiately unless
    a new sequence of `varBinds` are send back into running generator
    (supported since Python 2.6).

    Examples
    --------
    >>> from pysnmp.hlapi import *
    >>> g = setCmd(SnmpEngine(),
    ...            CommunityData('public'),
    ...            UdpTransportTarget(('demo.pysnmp.com', 161)),
    ...            ContextData(),
    ...            ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0), 'Linux i386'))
    >>> g
    (None, 0, 0, [ObjectType(ObjectIdentity(ObjectName('1.3.6.1.2.1.1.1.0')), DisplayString('Linux i386'))])
    >>>

    """

    loop = asyncio.get_event_loop()
    if loop.is_running():
        future = asyncio.ensure_future(
            _setCmd(
                snmpEngine, authData, transportTarget, contextData, *varBinds, **options
            )
        )
        return loop.run_until_complete(future)
    else:
        return loop.run_until_complete(
            _setCmd(
                snmpEngine, authData, transportTarget, contextData, *varBinds, **options
            )
        )


def nextCmd(
    snmpEngine: SnmpEngine,
    authData: "CommunityData | UsmUserData",
    transportTarget: AbstractTransportTarget,
    contextData: ContextData,
    *varBinds,
    **options
) -> (
    "tuple[errind.ErrorIndication, Integer32 | int, Integer32 | int, tuple[ObjectType]]"
):
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

    transportTarget : :py:class:`~pysnmp.hlapi.asyncio.UdpTransportTarget` or :py:class:`~pysnmp.hlapi.asyncio.Udp6TransportTarget`
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
    >>> g = nextCmd(SnmpEngine(),
    ...             CommunityData('public'),
    ...             UdpTransportTarget(('demo.pysnmp.com', 161)),
    ...             ContextData(),
    ...             ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr')))
    >>> g
    (None, 0, 0, [ObjectType(ObjectIdentity(ObjectName('1.3.6.1.2.1.1.1.0')), DisplayString('SunOS zeus.pysnmp.com 4.1.3_U1 1 sun4m'))])
    >>> g.send( [ ObjectType(ObjectIdentity('IF-MIB', 'ifInOctets')) ] )
    (None, 0, 0, [(ObjectName('1.3.6.1.2.1.2.2.1.10.1'), Counter32(284817787))])
    """

    loop = asyncio.get_event_loop()
    if loop.is_running():
        future = asyncio.ensure_future(
            _nextCmd(
                snmpEngine, authData, transportTarget, contextData, *varBinds, **options
            )
        )
        return loop.run_until_complete(future)
    else:
        return loop.run_until_complete(
            _nextCmd(
                snmpEngine, authData, transportTarget, contextData, *varBinds, **options
            )
        )


def bulkCmd(
    snmpEngine: SnmpEngine,
    authData: "CommunityData | UsmUserData",
    transportTarget: AbstractTransportTarget,
    contextData: ContextData,
    nonRepeaters: int,
    maxRepetitions: int,
    *varBinds,
    **options
) -> (
    "tuple[errind.ErrorIndication, Integer32 | int, Integer32 | int, tuple[ObjectType]]"
):
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
    >>> g = bulkCmd(SnmpEngine(),
    ...             CommunityData('public'),
    ...             UdpTransportTarget(('demo.pysnmp.com', 161)),
    ...             ContextData(),
    ...             0, 25,
    ...             ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr')))
    >>> g
    (None, 0, 0, [ObjectType(ObjectIdentity(ObjectName('1.3.6.1.2.1.1.1.0')), DisplayString('SunOS zeus.pysnmp.com 4.1.3_U1 1 sun4m'))])
    >>> g.send( [ ObjectType(ObjectIdentity('IF-MIB', 'ifInOctets')) ] )
    (None, 0, 0, [(ObjectName('1.3.6.1.2.1.2.2.1.10.1'), Counter32(284817787))])
    """

    loop = asyncio.get_event_loop()
    if loop.is_running():
        future = asyncio.ensure_future(
            _bulkCmd(
                snmpEngine,
                authData,
                transportTarget,
                contextData,
                nonRepeaters,
                maxRepetitions,
                *varBinds,
                **options
            )
        )
        return loop.run_until_complete(future)
    else:
        return loop.run_until_complete(
            _bulkCmd(
                snmpEngine,
                authData,
                transportTarget,
                contextData,
                nonRepeaters,
                maxRepetitions,
                *varBinds,
                **options
            )
        )
