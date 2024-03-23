#
# This file is part of pysnmp software.
#
# Copyright (c) 2023-2024, LeXtudio Inc. <support@lextudio.com>
# License: https://www.pysnmp.com/pysnmp/license.html
#
from typing import Iterator
from pysnmp.error import PySnmpError
from pysnmp.hlapi.asyncio.sync import *
from pysnmp.proto.errind import ErrorIndication

__all__ = ["Slim"]


class Slim:
    """Creates slim SNMP wrapper object.

    With PySNMP new design, `Slim` is the new high level API to wrap up v1/v2c.

    Parameters
    ----------
    version : :py:object:`int`
        Value of 1 maps to SNMP v1, while value of 2 maps to v2c.
        Default value is 2.

    Raises
    ------
    PySNMPError
        If the value of `version` is neither 1 nor 2.

    Examples
    --------
    >>> Slim()
    Slim(2)
    >>>

    """

    def __init__(self, version: int = 2):
        self.snmpEngine = SnmpEngine()
        if version not in (1, 2):
            raise PySnmpError(f"Not supported version {version}")
        self.version = version

    def close(self):
        """Closes the wrapper to release its resources."""
        if self.snmpEngine.transportDispatcher is not None:
            self.snmpEngine.transportDispatcher.closeDispatcher()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def get(
        self,
        communityName: str,
        address: str,
        port: int,
        *varBinds,
        timeout: int = 1,
        retries: int = 5,
    ) -> "Iterator[tuple[ErrorIndication, Integer32 | int, Integer32 | int, tuple[ObjectType]]]":
        """
        Creates a generator to perform SNMP GET query.

        When iterator gets advanced by :py:mod:`asyncio` main loop,
        SNMP GET request is send (:RFC:`1905#section-4.2.1`).
        The iterator yields :py:class:`asyncio.get_running_loop().create_future()` which gets done whenever
        response arrives or error occurs.

        Parameters
        ----------
        communityName : :py:obj:`str`
            Community name.

        address : :py:obj:`str`
            IP address or domain name.

        port : :py:obj:`int`
            Remote SNMP engine port number.

        *varBinds : :py:class:`~pysnmp.smi.rfc1902.ObjectType`
            One or more class instances representing MIB variables to place
            into SNMP request.

        timeout : :py:obj:`int`, optional
            Timeout value in seconds (default is 1).

        retries : :py:obj:`int`, optional
            Number of retries (default is 5).

        Yields
        ------
        errorIndication : :py:class:`~pysnmp.proto.errind.ErrorIndication`
            True value indicates SNMP engine error.

        errorStatus : :py:obj:`str`
            True value indicates SNMP PDU error.

        errorIndex : :py:obj:`int`
            Non-zero value refers to `varBinds[errorIndex-1]`.

        varBinds : :py:obj:`tuple`
            A sequence of :py:class:`~pysnmp.smi.rfc1902.ObjectType` class
            instances representing MIB variables returned in SNMP response.

        Raises
        ------
        PySnmpError
            Or its derivative indicating that an error occurred while
            performing SNMP operation.

        Examples
        --------
        >>> from pysnmp.hlapi.asyncio.sync.slim import Slim
        >>> with Slim() as slim:
        ...     errorIndication, errorStatus, errorIndex, varBinds = next(slim.get(
        ...         'public',
        ...         'demo.pysnmp.com',
        ...         161,
        ...         ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0))
        ...     ))
        ...     print(errorIndication, errorStatus, errorIndex, varBinds)
        (None, 0, 0, [ObjectType(ObjectIdentity(ObjectName('1.3.6.1.2.1.1.1.0')), DisplayString('SunOS zeus.pysnmp.com 4.1.3_U1 1 sun4m'))])
        >>>
        """

        return getCmd(
            self.snmpEngine,
            CommunityData(communityName, mpModel=self.version - 1),
            Udp6TransportTarget((address, port), timeout, retries)
            if ":" in address
            else UdpTransportTarget((address, port), timeout, retries),
            ContextData(),
            *varBinds,
        )

    def next(
        self,
        communityName: str,
        address: str,
        port: int,
        *varBinds,
        timeout: int = 1,
        retries: int = 5,
    ) -> "Iterator[tuple[ErrorIndication, Integer32 | int, Integer32 | int, tuple[ObjectType]]]":
        """
        Creates a generator to perform SNMP GETNEXT query.

        When iterator gets advanced by :py:mod:`asyncio` main loop,
        SNMP GETNEXT request is send (:RFC:`1905#section-4.2.2`).
        The iterator yields :py:class:`~asyncio.get_running_loop().create_future()` which gets done whenever
        response arrives or error occurs.

        Parameters
        ----------
        communityName : :py:obj:`str`
            Community name.

        address : :py:obj:`str`
            IP address or domain name.

        port : :py:obj:`int`
            Remote SNMP engine port number.

        *varBinds : :py:class:`~pysnmp.smi.rfc1902.ObjectType`
            One or more class instances representing MIB variables to place
            into SNMP request.

        timeout : :py:obj:`int`, optional
            Timeout value in seconds. Default is 1.

        retries : :py:obj:`int`, optional
            Number of retries. Default is 5.

        Yields
        ------
        errorIndication : :py:class:`~pysnmp.proto.errind.ErrorIndication`
            True value indicates SNMP engine error.

        errorStatus : :py:obj:`str`
            True value indicates SNMP PDU error.

        errorIndex : :py:obj:`int`
            Non-zero value refers to `varBinds[errorIndex-1]`

        varBinds : :py:obj:`tuple`
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
        >>> from pysnmp.hlapi.asyncio.sync.slim import Slim
        >>> with Slim() as slim:
        ...     errorIndication, errorStatus, errorIndex, varBinds = next(slim.next(
        ...         'public',
        ...         'demo.pysnmp.com',
        ...         161,
        ...         ObjectType(ObjectIdentity('SNMPv2-MIB', 'system'))
        ...     ))
        ...     print(errorIndication, errorStatus, errorIndex, varBinds)
        >>>
        (None, 0, 0, [[ObjectType(ObjectIdentity('1.3.6.1.2.1.1.1.0'), DisplayString('Linux i386'))]])
        >>>
        """
        return nextCmd(
            self.snmpEngine,
            CommunityData(communityName, mpModel=self.version - 1),
            Udp6TransportTarget((address, port), timeout, retries)
            if ":" in address
            else UdpTransportTarget((address, port), timeout, retries),
            ContextData(),
            *varBinds,
        )

    def bulk(
        self,
        communityName: str,
        address: str,
        port: int,
        nonRepeaters: int,
        maxRepetitions: int,
        *varBinds,
        timeout: int = 1,
        retries: int = 5,
    ) -> "Iterator[tuple[ErrorIndication, Integer32 | int, Integer32 | int, tuple[ObjectType]]]":
        r"""Creates a generator to perform SNMP GETBULK query.

        When iterator gets advanced by :py:mod:`asyncio` main loop,
        SNMP GETBULK request is send (:RFC:`1905#section-4.2.3`).
        The iterator yields :py:class:`asyncio.get_running_loop().create_future()` which gets done whenever
        response arrives or error occurs.

        Parameters
        ----------
        communityName : :py:obj:`str`
            Community name.

        address : :py:obj:`str`
            IP address or domain name.

        port : :py:obj:`int`
            Remote SNMP engine port number.

        nonRepeaters : :py:obj:`int`
            One MIB variable is requested in response for the first
            `nonRepeaters` MIB variables in request.

        maxRepetitions : :py:obj:`int`
            `maxRepetitions` MIB variables are requested in response for each
            of the remaining MIB variables in the request (e.g. excluding
            `nonRepeaters`). Remote SNMP engine may choose lesser value than
            requested.

        \*varBinds : :py:class:`~pysnmp.smi.rfc1902.ObjectType`
            One or more class instances representing MIB variables to place
            into SNMP request.

        timeout : :py:obj:`int`, optional
            Timeout value in seconds. Default is 1.

        retries : :py:obj:`int`, optional
            Number of retries. Default is 5.

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
        >>> from pysnmp.hlapi.asyncio.sync.slim import Slim
        >>> with Slim() as slim:
        ...     errorIndication, errorStatus, errorIndex, varBinds = next(slim.bulk(
        ...         'public',
        ...         'demo.pysnmp.com',
        ...         161,
        ...         0,
        ...         2,
        ...         ObjectType(ObjectIdentity('SNMPv2-MIB', 'system'))
        ...     ))
        ...     print(errorIndication, errorStatus, errorIndex, varBinds)
        >>>
        (None, 0, 0, [[ObjectType(ObjectIdentity(ObjectName('1.3.6.1.2.1.1.1.0')), DisplayString('SunOS zeus.pysnmp.com 4.1.3_U1 1 sun4m'))], [ObjectType(ObjectIdentity(ObjectName('1.3.6.1.2.1.1.2.0')), ObjectIdentifier('1.3.6.1.4.1.424242.1.1'))]])
        >>>

        """

        version = self.version - 1
        if version == 0:
            raise PySnmpError("Cannot send V2 PDU on V1 session")
        return bulkCmd(
            self.snmpEngine,
            CommunityData(communityName, mpModel=version),
            Udp6TransportTarget((address, port), timeout, retries)
            if ":" in address
            else UdpTransportTarget((address, port), timeout, retries),
            ContextData(),
            nonRepeaters,
            maxRepetitions,
            *varBinds,
        )

    def set(
        self,
        communityName: str,
        address: str,
        port: int,
        *varBinds,
        timeout: int = 1,
        retries: int = 5,
    ) -> "Iterator[tuple[ErrorIndication, Integer32 | int, Integer32 | int, tuple[ObjectType]]]":
        """
        Creates a generator to perform SNMP SET query.

        When iterator gets advanced by :py:mod:`asyncio` main loop,
        SNMP SET request is send (:RFC:`1905#section-4.2.5`).
        The iterator yields :py:class:`asyncio.get_running_loop().create_future()` which gets done whenever
        response arrives or error occurs.

        Parameters
        ----------
        communityName : :py:obj:`str`
            Community name.

        address : :py:obj:`str`
            IP address or domain name.

        port : :py:obj:`int`
            Remote SNMP engine port number.

        *varBinds : :py:class:`~pysnmp.smi.rfc1902.ObjectType`
            One or more class instances representing MIB variables to place
            into SNMP request.

        timeout : :py:obj:`int`, optional
            Timeout value in seconds. Default is 1.

        retries : :py:obj:`int`, optional
            Number of retries. Default is 5.

        Yields
        ------
        errorIndication : :py:class:`~pysnmp.proto.errind.ErrorIndication`
            True value indicates SNMP engine error.
        errorStatus : :py:obj:`str`
            True value indicates SNMP PDU error.
        errorIndex : :py:obj:`int`
            Non-zero value refers to `varBinds[errorIndex-1]`
        varBinds : :py:class:`~pysnmp.smi.rfc1902.ObjectType`
            A sequence of :py:class:`~pysnmp.smi.rfc1902.ObjectType` class
            instances representing MIB variables returned in SNMP response.

        Raises
        ------
        PySnmpError
            Or its derivative indicating that an error occurred while
            performing SNMP operation.

        Examples
        --------
        >>> from pysnmp.hlapi.asyncio.sync.slim import Slim
        >>> with Slim() as slim:
        ...     errorIndication, errorStatus, errorIndex, varBinds = next(slim.set(
        ...         'public',
        ...         'demo.pysnmp.com',
        ...         161,
        ...         ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0), 'Linux i386')
        ...     ))
        ...     print(errorIndication, errorStatus, errorIndex, varBinds)
        >>>
        (None, 0, 0, [ObjectType(ObjectIdentity(ObjectName('1.3.6.1.2.1.1.1.0')), DisplayString('Linux i386'))])
        >>>
        """

        return setCmd(
            self.snmpEngine,
            CommunityData(communityName, mpModel=self.version - 1),
            Udp6TransportTarget((address, port), timeout, retries)
            if ":" in address
            else UdpTransportTarget((address, port), timeout, retries),
            ContextData(),
            *varBinds,
        )
