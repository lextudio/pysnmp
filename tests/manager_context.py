# manager_context.py
import asyncio
from typing import List, Tuple


from pysnmp.entity.rfc3413 import ntfrcv
from pysnmp.hlapi.v3arch.asyncio import *
from pysnmp.carrier.asyncio.dgram import udp
from pysnmp.entity import engine, config
from pysnmp.proto.api import v2c

# Set the port to 1622 instead of 162, because 162 is a
# privileged port and requires root access
MANAGER_PORT = 1622


async def start_manager(
    message_count: List[int],
) -> Tuple[SnmpEngine, ntfrcv.NotificationReceiver]:
    # Create SNMP engine
    snmpEngine = engine.SnmpEngine()

    # Transport setup

    # UDP over IPv4
    config.add_transport(
        snmpEngine,
        udp.DOMAIN_NAME,
        udp.UdpTransport().open_server_mode(("localhost", MANAGER_PORT)),
    )

    # SNMPv1/2c setup

    # SecurityName <-> CommunityName mapping
    config.add_v1_system(snmpEngine, "public", "public")

    # SNMPv3/USM setup

    # user: usr-md5-des, auth: MD5, priv DES
    config.add_v3_user(
        snmpEngine,
        "usr-md5-des",
        config.USM_AUTH_HMAC96_MD5,
        "authkey1",
        config.USM_PRIV_CBC56_DES,
        "privkey1",
    )

    # user: usr-md5-des, auth: MD5, priv DES, securityEngineId: 8000000001020304
    # this USM entry is used for TRAP receiving purposes
    config.add_v3_user(
        snmpEngine,
        "usr-md5-des",
        config.USM_AUTH_HMAC96_MD5,
        "authkey1",
        config.USM_PRIV_CBC56_DES,
        "privkey1",
        securityEngineId=v2c.OctetString(hexValue="8000000001020304"),
    )

    # user: usr-none-none, auth: NONE, priv: NONE
    # this USM entry is used for TRAP receiving purposes
    config.add_v3_user(
        snmpEngine,
        "usr-none-none",
        config.USM_AUTH_NONE,
        config.USM_PRIV_NONE,
        securityEngineId=v2c.OctetString(hexValue="8000000001020305"),
    )

    # Callback function for receiving notifications
    # noinspection PyUnusedLocal,PyUnusedLocal,PyUnusedLocal
    def cbFun(
        snmpEngine, stateReference, contextEngineId, contextName, varBinds, cbCtx
    ):
        message_count[0] += 1

    # Register SNMP Application at the SNMP engine
    receiver = ntfrcv.NotificationReceiver(snmpEngine, cbFun)

    # Run I/O dispatcher which would receive queries and send confirmations
    snmpEngine.transport_dispatcher.job_started(1)  # this job would never finish

    snmpEngine.open_dispatcher()

    # Wait for the manager to start
    await asyncio.sleep(1)

    # return the engine
    return snmpEngine, receiver


class ManagerContextManager:
    """
    A context manager for managing the lifecycle of an SNMP test manager.

    Usage:
    async with ManagerContextManager() as manager:
        # Perform operations with the manager

    When the context is entered, the manager is started using the `start_manager()` function.
    When the context is exited, the manger's transport dispatcher is stopped and closed.

    Note: The `start_manager()` function and the `transportDispatcher` attribute are not defined in this code snippet.
    """

    manager: SnmpEngine
    receiver: ntfrcv.NotificationReceiver
    message_count: List[int]

    async def __aenter__(self):
        self.message_count = [0]
        self.manager, self.receiver = await start_manager(self.message_count)
        return self.manager, self.message_count

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.receiver.close(self.manager)

        self.manager.transport_dispatcher.job_finished(1)
        self.manager.close_dispatcher()
        self.manager._close()
