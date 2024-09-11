#
# This file is part of pysnmp software.
#
# Copyright (c) 2005-2020, Ilya Etingof <etingof@gmail.com>
#
# Copyright (c) 2022-2024, LeXtudio Inc. <support@lextudio.com>
# License: https://www.pysnmp.com/pysnmp/license.html
#
# All code in this file belongs to obsolete, compatibility wrappers.
# Never use interfaces below for new applications!
#
from pysnmp.hlapi.asyncio import *
from pysnmp.hlapi.asyncio import sync
from pysnmp.hlapi.varbinds import *
from pysnmp.hlapi.lcd import *
from pyasn1.type import univ

__all__ = ["CommandGenerator", "MibVariable"]

MibVariable = ObjectIdentity


class CommandGenerator:
    _null = univ.Null("")

    def __init__(self, snmpEngine=None, asynCmdGen=None):
        # compatibility attributes
        self.snmpEngine = snmpEngine or SnmpEngine()

    def getCmd(self, authData, transportTarget, *varNames, **kwargs):
        if "lookupNames" not in kwargs:
            kwargs["lookupNames"] = False
        if "lookupValues" not in kwargs:
            kwargs["lookupValues"] = False
        return sync.getCmd(
            self.snmpEngine,
            authData,
            transportTarget,
            ContextData(kwargs.get("contextEngineId"), kwargs.get("contextName", b"")),
            *[(x, self._null) for x in varNames],
            **kwargs
        )

    def setCmd(self, authData, transportTarget, *varBinds, **kwargs):
        if "lookupNames" not in kwargs:
            kwargs["lookupNames"] = False
        if "lookupValues" not in kwargs:
            kwargs["lookupValues"] = False
        return sync.setCmd(
            self.snmpEngine,
            authData,
            transportTarget,
            ContextData(kwargs.get("contextEngineId"), kwargs.get("contextName", b"")),
            *varBinds,
            **kwargs
        )

    def nextCmd(self, authData, transportTarget, *varNames, **kwargs):
        if "lookupNames" not in kwargs:
            kwargs["lookupNames"] = False
        if "lookupValues" not in kwargs:
            kwargs["lookupValues"] = False
        if "lexicographicMode" not in kwargs:
            kwargs["lexicographicMode"] = False
        errorIndication, errorStatus, errorIndex = None, 0, 0
        varBindTable = []
        for errorIndication, errorStatus, errorIndex, varBinds in sync.walkCmd(
            self.snmpEngine,
            authData,
            transportTarget,
            ContextData(kwargs.get("contextEngineId"), kwargs.get("contextName", b"")),
            *[(x, self._null) for x in varNames],
            **kwargs
        ):
            if errorIndication or errorStatus:
                return errorIndication, errorStatus, errorIndex, varBinds

            varBindTable.append(varBinds)

        return errorIndication, errorStatus, errorIndex, varBindTable

    def bulkCmd(
        self,
        authData,
        transportTarget,
        nonRepeaters,
        maxRepetitions,
        *varNames,
        **kwargs
    ):
        if "lookupNames" not in kwargs:
            kwargs["lookupNames"] = False
        if "lookupValues" not in kwargs:
            kwargs["lookupValues"] = False
        if "lexicographicMode" not in kwargs:
            kwargs["lexicographicMode"] = False
        errorIndication, errorStatus, errorIndex = None, 0, 0
        varBindTable = []
        for errorIndication, errorStatus, errorIndex, varBinds in sync.bulkWalkCmd(
            self.snmpEngine,
            authData,
            transportTarget,
            ContextData(kwargs.get("contextEngineId"), kwargs.get("contextName", b"")),
            nonRepeaters,
            maxRepetitions,
            *[(x, self._null) for x in varNames],
            **kwargs
        ):
            if errorIndication or errorStatus:
                return errorIndication, errorStatus, errorIndex, varBinds

            varBindTable.append(varBinds)

        return errorIndication, errorStatus, errorIndex, varBindTable
