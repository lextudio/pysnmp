#
# This file is part of pysnmp software.
#
# Copyright (c) 2023, LeXtudio Inc. <support@lextudio.com>
# License: https://www.pysnmp.com/pysnmp/license.html
#
from pysnmp.error import PySnmpError
from pysnmp.hlapi.v3arch.asyncio import *

__all__ = ['Slim']

class Slim:
    """Creates slim SNMP wrapper object.

    With PySNMP new design, `Slim` is the new high level API to wrap up v1/v2c.

    Parameters
    ----------
    version : int
        Value of 1 maps to SNMP v1, while value of 2 maps to v2c.
        Default value is 2.

    Examples
    --------
    >>> Slim()
    Slim(1)
    >>>

    """

    def __init__(self, version=2):
        self.snmpEngine = SnmpEngine()
        if version not in (1, 2):
            raise PySnmpError('Not supported version {version}')
        self.version = version

    def close(self):
        self.snmpEngine.transportDispatcher.closeDispatcher()

    async def get(self, communityName, address, port, id):
        get_result = await getCmd(
            self.snmpEngine,
            CommunityData(communityName, mpModel=self.version - 1),
            UdpTransportTarget((address, port)),
            ContextData(),
            ObjectType(id),
        )

        return await get_result

    async def next(self, communityName, address, port, id):
        next_result = await nextCmd(
            self.snmpEngine,
            CommunityData(communityName, mpModel=self.version - 1),
            UdpTransportTarget((address, port)),
            ContextData(),
            ObjectType(id),
        )

        return await next_result

    async def bulk(self, communityName, address, port, nonRepeaters, maxRepetitions, id):
        version = self.version - 1
        if version == 0:
            raise PySnmpError('Cannot send V2 PDU on V1 session')
        bulk_result = await bulkCmd(
            self.snmpEngine,
            CommunityData(communityName, mpModel=version),
            UdpTransportTarget((address, port)),
            ContextData(),
            nonRepeaters,
            maxRepetitions,
            ObjectType(id),
        )

        return await bulk_result

    async def set(self, communityName, address, port, id, data):
        set_result = await setCmd(
            self.snmpEngine,
            CommunityData(communityName, mpModel=self.version - 1),
            UdpTransportTarget((address, port)),
            ContextData(),
            ObjectType(id, data),
        )

        return await set_result

