#
# This file is part of pysnmp software.
#
# Copyright (c) 2005-2020, Ilya Etingof <etingof@gmail.com>
# License: https://www.pysnmp.com/pysnmp/license.html
#
import os
import shutil
import sys
import tempfile
from typing import Any, Dict
import warnings


from pyasn1.type import univ
from pysnmp import debug, error
from pysnmp.carrier.base import AbstractTransportAddress, AbstractTransportDispatcher
from pysnmp.entity import observer
from pysnmp.proto.acmod import rfc3415, void
from pysnmp.proto.mpmod.base import AbstractMessageProcessingModel
from pysnmp.proto.mpmod.rfc2576 import (
    SnmpV1MessageProcessingModel,
    SnmpV2cMessageProcessingModel,
)
from pysnmp.proto.mpmod.rfc3412 import SnmpV3MessageProcessingModel
from pysnmp.proto.rfc1902 import OctetString
from pysnmp.proto.rfc3412 import MsgAndPduDispatcher
from pysnmp.proto.secmod.base import AbstractSecurityModel
from pysnmp.proto.secmod.rfc2576 import SnmpV1SecurityModel, SnmpV2cSecurityModel
from pysnmp.proto.secmod.rfc3414 import SnmpUSMSecurityModel
from pysnmp.smi.builder import MibBuilder

__all__ = ["SnmpEngine"]


class SnmpEngine:
    """Creates SNMP engine object.

    SNMP engine object is central in SNMP v3 architecture. It is an umbrella
    object that coordinates interactions between all parts of SNMP v3 system.
    See :RFC:`3412#section-2.1` (where it is termed *The Dispatcher*).

    With PySNMP design, `SnmpEngine` is the only stateful object, all SNMP
    v3 operations require an instance of SNMP engine. Users do not normally
    request services directly from `SnmpEngine`, but pass it around to
    other PySNMP interfaces.

    It is possible to run multiple instances of `SnmpEngine` in the
    application. In a multithreaded environment, each thread that
    works with SNMP must have its own `SnmpEngine` instance.

    Parameters
    ----------
    snmpEngineID : :py:class:`~pysnmp.proto.rfc1902.OctetString`
        Unique and unambiguous identifier of an SNMP engine.
        If not given, `snmpEngineID` is autogenerated and stored on
        the filesystem. See :RFC:`3411#section-3.1.1`  for details.

    Examples
    --------
    >>> SnmpEngine()
    SnmpEngine(snmpEngineID=OctetString(hexValue='0x80004fb80567726f6d6d69742'))
    >>>

    """

    transport_dispatcher: "AbstractTransportDispatcher"
    message_dispatcher: MsgAndPduDispatcher
    engine_id: OctetString
    cache: Dict[str, Any]
    security_models: Dict[int, AbstractSecurityModel]
    message_processing_subsystems: Dict[univ.Integer, AbstractMessageProcessingModel]
    access_control_model: Dict[int, "void.Vacm | rfc3415.Vacm"]

    def __init__(
        self,
        snmpEngineID: "OctetString | None" = None,
        maxMessageSize: int = 65507,
        msgAndPduDsp: "MsgAndPduDispatcher | None" = None,
    ):
        """Create an SNMP engine object."""
        self.cache = {}

        self.observer = observer.MetaObserver()

        if msgAndPduDsp is None:
            self.message_dispatcher = MsgAndPduDispatcher()
        else:
            self.message_dispatcher = msgAndPduDsp
        self.message_processing_subsystems = {
            SnmpV1MessageProcessingModel.MESSAGE_PROCESSING_MODEL_ID: SnmpV1MessageProcessingModel(),
            SnmpV2cMessageProcessingModel.MESSAGE_PROCESSING_MODEL_ID: SnmpV2cMessageProcessingModel(),
            SnmpV3MessageProcessingModel.MESSAGE_PROCESSING_MODEL_ID: SnmpV3MessageProcessingModel(),
        }
        self.security_models = {
            SnmpV1SecurityModel.SECURITY_MODEL_ID: SnmpV1SecurityModel(),
            SnmpV2cSecurityModel.SECURITY_MODEL_ID: SnmpV2cSecurityModel(),
            SnmpUSMSecurityModel.SECURITY_MODEL_ID: SnmpUSMSecurityModel(),
        }
        self.access_control_model: dict[int, "void.Vacm | rfc3415.Vacm"] = {
            void.Vacm.ACCESS_MODEL_ID: void.Vacm(),
            rfc3415.Vacm.ACCESS_MODEL_ID: rfc3415.Vacm(),
        }

        self.transport_dispatcher = None  # type: ignore

        if self.message_dispatcher.mib_instrum_controller is None:
            raise error.PySnmpError("MIB instrumentation does not yet exist")
        (
            snmpEngineMaxMessageSize,
        ) = self.get_mib_builder().import_symbols(  # type: ignore
            "__SNMP-FRAMEWORK-MIB", "snmpEngineMaxMessageSize"
        )
        snmpEngineMaxMessageSize.syntax = snmpEngineMaxMessageSize.syntax.clone(
            maxMessageSize
        )
        (snmpEngineBoots,) = self.get_mib_builder().import_symbols(  # type: ignore
            "__SNMP-FRAMEWORK-MIB", "snmpEngineBoots"
        )
        snmpEngineBoots.syntax += 1
        (origSnmpEngineID,) = self.get_mib_builder().import_symbols(  # type: ignore
            "__SNMP-FRAMEWORK-MIB", "snmpEngineID"
        )

        if snmpEngineID is None:
            self.snmpEngineID = origSnmpEngineID.syntax
        else:
            origSnmpEngineID.syntax = origSnmpEngineID.syntax.clone(snmpEngineID)
            self.snmpEngineID = origSnmpEngineID.syntax

            debug.logger & debug.FLAG_APP and debug.logger(
                "SnmpEngine: using custom SNMP Engine ID: %s"
                % self.snmpEngineID.prettyPrint()
            )

            # Attempt to make some of snmp Engine settings persistent.
            # This should probably be generalized as a non-volatile MIB store.

            persistentPath = os.path.join(
                tempfile.gettempdir(), "__pysnmp", self.snmpEngineID.prettyPrint()
            )

            debug.logger & debug.FLAG_APP and debug.logger(
                "SnmpEngine: using persistent directory: %s" % persistentPath
            )

            if not os.path.exists(persistentPath):
                try:
                    os.makedirs(persistentPath)
                except OSError:
                    return

            f = os.path.join(persistentPath, "boots")
            try:
                snmpEngineBoots.syntax = snmpEngineBoots.syntax.clone(open(f).read())
            except Exception:
                pass

            try:
                snmpEngineBoots.syntax += 1
            except Exception:
                snmpEngineBoots.syntax = snmpEngineBoots.syntax.clone(1)

            try:
                fd, fn = tempfile.mkstemp(dir=persistentPath)
                os.write(fd, snmpEngineBoots.syntax.prettyPrint().encode("iso-8859-1"))
                os.close(fd)
                shutil.move(fn, f)
            except Exception:
                debug.logger & debug.FLAG_APP and debug.logger(
                    "SnmpEngine: could not stored SNMP Engine Boots: %s"
                    % sys.exc_info()[1]
                )
            else:
                debug.logger & debug.FLAG_APP and debug.logger(
                    "SnmpEngine: stored SNMP Engine Boots: %s"
                    % snmpEngineBoots.syntax.prettyPrint()
                )

    def __repr__(self):
        """Return a string representation of the SNMP engine object."""
        return f"{self.__class__.__name__}(snmpEngineID={self.snmpEngineID!r})"

    def _close(self):
        """
        Close the SNMP engine to test memory leak.

        This method is intended for unit testing purposes only.
        It closes the SNMP engine and checks if all associated resources are released.
        """
        for securityModel in self.security_models.values():
            securityModel._close()

    def open_dispatcher(self, timeout: float = 0):
        """
        Open the dispatcher used by SNMP engine.

        This method is called when SNMP engine is ready to process SNMP
        messages. It opens the dispatcher and starts processing incoming
        messages.
        """
        if self.transport_dispatcher:
            self.transport_dispatcher.run_dispatcher(timeout)

    def close_dispatcher(self):
        """
        Close the dispatcher used by SNMP engine.

        This method is called when SNMP engine is no longer needed. It
        releases all resources allocated by the engine.
        """
        if self.transport_dispatcher:
            self.transport_dispatcher.close_dispatcher()
            self.unregister_transport_dispatcher()

    # Transport dispatcher bindings

    def __receive_message_callback(
        self,
        transportDispatcher: AbstractTransportDispatcher,
        transportDomain: "tuple[int, ...]",
        transportAddress: AbstractTransportAddress,
        wholeMsg,
    ):
        self.message_dispatcher.receive_message(
            self, transportDomain, transportAddress, wholeMsg
        )

    def __receive_timer_tick_callback(self, timeNow: float):
        self.message_dispatcher.receive_timer_tick(self, timeNow)
        for mpHandler in self.message_processing_subsystems.values():
            mpHandler.receive_timer_tick(self, timeNow)
        for smHandler in self.security_models.values():
            smHandler.receive_timer_tick(self, timeNow)

    def register_transport_dispatcher(
        self,
        transportDispatcher: AbstractTransportDispatcher,
        recvId: "tuple[int, ...] | str | None" = None,
    ):
        """Register transport dispatcher."""
        if (
            self.transport_dispatcher is not None
            and self.transport_dispatcher is not transportDispatcher
        ):
            raise error.PySnmpError("Transport dispatcher already registered")
        transportDispatcher.register_recv_callback(
            self.__receive_message_callback, recvId
        )
        if self.transport_dispatcher is None:
            transportDispatcher.register_timer_callback(
                self.__receive_timer_tick_callback
            )
            self.transport_dispatcher = transportDispatcher

    def unregister_transport_dispatcher(self, recvId: "tuple[int, ...] | None" = None):
        """Remove transport dispatcher."""
        if self.transport_dispatcher is None:
            raise error.PySnmpError("Transport dispatcher not registered")
        self.transport_dispatcher.unregister_recv_callback(recvId)
        self.transport_dispatcher.unregister_timer_callback()
        self.transport_dispatcher = None  # type: ignore

    def get_mib_builder(self) -> MibBuilder:
        """Get MIB builder."""
        return self.message_dispatcher.mib_instrum_controller.get_mib_builder()

    # User app may attach opaque objects to SNMP Engine
    def set_user_context(self, **kwargs):
        """Attach user context to the SNMP engine."""
        self.cache.update({"__%s" % k: kwargs[k] for k in kwargs})

    def get_user_context(self, arg) -> "dict[str, Any] | None":
        """Get user context."""
        return self.cache.get("__%s" % arg)

    def delete_user_context(self, arg):
        """Delete user context."""
        try:
            del self.cache["__%s" % arg]
        except KeyError:
            pass

    # compatibility with legacy code
    # Old to new attribute mapping
    deprecated_attributes = {
        "transportDispatcher": "transport_dispatcher",
        "openDispatcher": "open_dispatcher",
        "closeDispatcher": "close_dispatcher",
        "msgAndPduDsp": "message_dispatcher",
    }

    def __getattr__(self, attr: str):
        if new_attr := self.deprecated_attributes.get(attr):
            warnings.warn(
                f"{attr} is deprecated. Please use {new_attr} instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            return getattr(self, new_attr)
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{attr}'"
        )
