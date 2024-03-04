from pysnmp.entity.engine import SnmpEngine

from pysnmp.hlapi.v3arch.auth import CommunityData, UsmUserData
from pysnmp.hlapi.v3arch.context import ContextData
from pysnmp.hlapi.transport import AbstractTransportTarget
from pysnmp.hlapi.v3arch.asyncio.ntforg import sendNotification as _sendNotification

from pysnmp.proto import errind
from pysnmp.proto.rfc1902 import Integer32
from pysnmp.smi.rfc1902 import ObjectType

import asyncio

__all__ = ["sendNotification"]


def sendNotification(
    snmpEngine: SnmpEngine,
    authData: "CommunityData | UsmUserData",
    transportTarget: AbstractTransportTarget,
    contextData: ContextData,
    notifyType,
    varBinds,
    **options
) -> (
    "tuple[errind.ErrorIndication, Integer32 | int, Integer32 | int, tuple[ObjectType]]"
):
    r"""Creates a generator to send one or more SNMP notifications.

    On each iteration, new SNMP TRAP or INFORM notification is send
    (:RFC:`1905#section-4,2,6`). The iterator blocks waiting for
    INFORM acknowledgement to arrive or error to occur.

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

    notifyType : str
        Indicates type of notification to be sent. Recognized literal
        values are *trap* or *inform*.

    varBinds: tuple
        Single :py:class:`~pysnmp.smi.rfc1902.NotificationType` class instance
        representing a minimum sequence of MIB variables required for
        particular notification type.
        Alternatively, a sequence of :py:class:`~pysnmp.smi.rfc1902.ObjectType`
        objects could be passed instead. In the latter case it is up to
        the user to ensure proper Notification PDU contents.

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
    The `sendNotification` generator will be exhausted immidiately unless
    an instance of :py:class:`~pysnmp.smi.rfc1902.NotificationType` class
    or a sequence of :py:class:`~pysnmp.smi.rfc1902.ObjectType` `varBinds`
    are send back into running generator (supported since Python 2.6).

    Examples
    --------
    >>> from pysnmp.hlapi import *
    >>> g = sendNotification(SnmpEngine(),
    ...                      CommunityData('public'),
    ...                      UdpTransportTarget(('demo.pysnmp.com', 162)),
    ...                      ContextData(),
    ...                      'trap',
    ...                      NotificationType(ObjectIdentity('IF-MIB', 'linkDown')))
    >>> g
    (None, 0, 0, [])
    >>>

    """

    loop = asyncio.get_event_loop()
    if loop.is_running():
        future = asyncio.ensure_future(
            _sendNotification(
                snmpEngine,
                authData,
                transportTarget,
                contextData,
                notifyType,
                varBinds,
                **options
            )
        )
        return loop.run_until_complete(future)
    else:
        return loop.run_until_complete(
            _sendNotification(
                snmpEngine,
                authData,
                transportTarget,
                contextData,
                notifyType,
                varBinds,
                **options
            )
        )
