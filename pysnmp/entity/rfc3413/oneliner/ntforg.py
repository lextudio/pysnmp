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
from pysnmp.entity import config
from pysnmp.entity.rfc3413 import context

__all__ = ["NotificationOriginator", "MibVariable"]

MibVariable = ObjectIdentity


class ErrorIndicationReturn:
    def __init__(self, *vars):
        self.__vars = vars

    def __getitem__(self, i):
        return self.__vars[i]

    def __nonzero__(self):
        return bool(self)

    def __bool__(self):
        return bool(self.__vars[0])

    def __str__(self):
        return str(self.__vars[0])


class NotificationOriginator:
    vbProcessor = NotificationOriginatorVarBinds()

    def __init__(self, snmpEngine=None, snmpContext=None, asynNtfOrg=None):
        # compatibility attributes
        self.snmpEngine = snmpEngine or SnmpEngine()
        self.mibViewController = self.vbProcessor.getMibViewController(self.snmpEngine)

    # the varBinds parameter is legacy, use NotificationType instead

    def sendNotification(
        self,
        authData,
        transportTarget,
        notifyType,
        notificationType,
        *varBinds,
        **kwargs
    ):
        if "lookupNames" not in kwargs:
            kwargs["lookupNames"] = False
        if "lookupValues" not in kwargs:
            kwargs["lookupValues"] = False
        if not isinstance(
            notificationType, (ObjectIdentity, ObjectType, NotificationType)
        ):
            if isinstance(notificationType[0], tuple):
                # legacy
                notificationType = ObjectIdentity(
                    notificationType[0][0],
                    notificationType[0][1],
                    *notificationType[1:]
                )
            else:
                notificationType = ObjectIdentity(notificationType)

        if not isinstance(notificationType, NotificationType):
            notificationType = NotificationType(notificationType)

        (errorIndication, errorStatus, errorIndex, rspVarBinds) = sync.sendNotification(
            self.snmpEngine,
            authData,
            transportTarget,
            ContextData(kwargs.get("contextEngineId"), kwargs.get("contextName", b"")),
            notifyType,
            notificationType.addVarBinds(*varBinds),
            **kwargs
        )
        if notifyType == "inform":
            return errorIndication, errorStatus, errorIndex, rspVarBinds
        else:
            pass
