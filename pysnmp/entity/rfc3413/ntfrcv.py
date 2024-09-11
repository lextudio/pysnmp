#
# This file is part of pysnmp software.
#
# Copyright (c) 2005-2020, Ilya Etingof <etingof@gmail.com>
# License: https://www.pysnmp.com/pysnmp/license.html
#
import sys


from pysnmp import debug
from pysnmp.proto import error, rfc3411
from pysnmp.proto.api import v1, v2c  # backend is always SMIv2 compliant
from pysnmp.proto.proxy import rfc2576


# 3.4
class NotificationReceiver:
    SUPPORTED_PDU_TYPES = (
        v1.TrapPDU.tagSet,
        v2c.SNMPv2TrapPDU.tagSet,
        v2c.InformRequestPDU.tagSet,
    )

    def __init__(self, snmpEngine, cbFun, cbCtx=None):
        snmpEngine.msgAndPduDsp.registerContextEngineId(
            b"", self.SUPPORTED_PDU_TYPES, self.processPdu  # '' is a wildcard
        )

        self.__snmpTrapCommunity = ""
        self.__cbFun = cbFun
        self.__cbCtx = cbCtx

        def storeSnmpTrapCommunity(snmpEngine, execpoint, variables, cbCtx):
            self.__snmpTrapCommunity = variables.get("communityName", "")

        snmpEngine.observer.registerObserver(
            storeSnmpTrapCommunity, "rfc2576.processIncomingMsg"
        )

    def close(self, snmpEngine):
        snmpEngine.msgAndPduDsp.unregisterContextEngineId(b"", self.SUPPORTED_PDU_TYPES)
        self.__cbFun = self.__cbCtx = None

    def processPdu(
        self,
        snmpEngine,
        messageProcessingModel,
        securityModel,
        securityName,
        securityLevel,
        contextEngineId,
        contextName,
        pduVersion,
        PDU,
        maxSizeResponseScopedPDU,
        stateReference,
    ):
        # Agent-side API complies with SMIv2
        if messageProcessingModel == 0:
            origPdu = PDU
            PDU = rfc2576.v1ToV2(PDU, snmpTrapCommunity=self.__snmpTrapCommunity)
        else:
            origPdu = None

        errorStatus = "noError"
        errorIndex = 0
        varBinds = v2c.apiPDU.getVarBinds(PDU)

        debug.logger & debug.FLAG_APP and debug.logger(
            f"processPdu: stateReference {stateReference}, varBinds {varBinds}"
        )

        # 3.4
        if PDU.tagSet in rfc3411.CONFIRMED_CLASS_PDUS:
            # 3.4.1 --> no-op

            rspPDU = v2c.apiPDU.getResponse(PDU)

            # 3.4.2
            v2c.apiPDU.setErrorStatus(rspPDU, errorStatus)
            v2c.apiPDU.setErrorIndex(rspPDU, errorIndex)
            v2c.apiPDU.setVarBinds(rspPDU, varBinds)

            debug.logger & debug.FLAG_APP and debug.logger(
                f"processPdu: stateReference {stateReference}, confirm PDU {rspPDU.prettyPrint()}"
            )

            # Agent-side API complies with SMIv2
            if messageProcessingModel == 0:
                rspPDU = rfc2576.v2ToV1(rspPDU, origPdu)

            statusInformation = {}

            # 3.4.3
            try:
                snmpEngine.msgAndPduDsp.returnResponsePdu(
                    snmpEngine,
                    messageProcessingModel,
                    securityModel,
                    securityName,
                    securityLevel,
                    contextEngineId,
                    contextName,
                    pduVersion,
                    rspPDU,
                    maxSizeResponseScopedPDU,
                    stateReference,
                    statusInformation,
                )

            except error.StatusInformation:
                debug.logger & debug.FLAG_APP and debug.logger(
                    f"processPdu: stateReference {stateReference}, statusInformation {sys.exc_info()[1]}"
                )
                (
                    snmpSilentDrops,
                ) = snmpEngine.msgAndPduDsp.mibInstrumController.mibBuilder.importSymbols(
                    "__SNMPv2-MIB", "snmpSilentDrops"
                )
                snmpSilentDrops.syntax += 1

        elif PDU.tagSet in rfc3411.UNCONFIRMED_CLASS_PDUS:
            pass
        else:
            raise error.ProtocolError("Unexpected PDU class %s" % PDU.tagSet)

        debug.logger & debug.FLAG_APP and debug.logger(
            "processPdu: stateReference {}, user cbFun {}, cbCtx {}, varBinds {}".format(
                stateReference, self.__cbFun, self.__cbCtx, varBinds
            )
        )

        self.__cbFun(
            snmpEngine,
            stateReference,
            contextEngineId,
            contextName,
            varBinds,
            self.__cbCtx,
        )
