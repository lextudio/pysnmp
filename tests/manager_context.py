# manager_context.py
from pysnmp.entity.rfc3413 import ntfrcv
from pysnmp.hlapi import *
from pysnmp.carrier.asyncio.dgram import udp
from pysnmp.entity import engine, config
from pysnmp.proto.api import v2c

import asyncio

# Set the port to 1622 instead of 162, because 162 is a
# privileged port and requires root access
MANAGER_PORT = 1622


async def start_manager() -> SnmpEngine:
    # Create SNMP engine
    snmpEngine = engine.SnmpEngine()

    # Transport setup

    # UDP over IPv4
    config.addTransport(
        snmpEngine,
        udp.DOMAIN_NAME,
        udp.UdpTransport().openServerMode(("localhost", MANAGER_PORT)),
    )

    # SNMPv1/2c setup

    # SecurityName <-> CommunityName mapping
    config.addV1System(snmpEngine, "public", "public")

    # SNMPv3/USM setup

    # user: usr-md5-des, auth: MD5, priv DES
    config.addV3User(
        snmpEngine,
        "usr-md5-des",
        config.USM_AUTH_HMAC96_MD5,
        "authkey1",
        config.USM_PRIV_CBC56_DES,
        "privkey1",
    )

    # user: usr-md5-des, auth: MD5, priv DES, securityEngineId: 8000000001020304
    # this USM entry is used for TRAP receiving purposes
    config.addV3User(
        snmpEngine,
        "usr-md5-des",
        config.USM_AUTH_HMAC96_MD5,
        "authkey1",
        config.USM_PRIV_CBC56_DES,
        "privkey1",
        securityEngineId=v2c.OctetString(hexValue="8000000001020304"),
    )

    # Callback function for receiving notifications
    # noinspection PyUnusedLocal,PyUnusedLocal,PyUnusedLocal
    def cbFun(
        snmpEngine, stateReference, contextEngineId, contextName, varBinds, cbCtx
    ):
        print(
            'Notification from ContextEngineId "{}", ContextName "{}"'.format(
                contextEngineId.prettyPrint(), contextName.prettyPrint()
            )
        )
        for name, val in varBinds:
            print(f"{name.prettyPrint()} = {val.prettyPrint()}")

    # Register SNMP Application at the SNMP engine
    ntfrcv.NotificationReceiver(snmpEngine, cbFun)

    # Run I/O dispatcher which would receive queries and send confirmations
    snmpEngine.transportDispatcher.jobStarted(1)  # this job would never finish

    snmpEngine.transportDispatcher.runDispatcher()

    # Wait for the manager to start
    await asyncio.sleep(1)

    # return the engine
    return snmpEngine


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

    async def __aenter__(self):
        self.manager = await start_manager()
        return self.manager

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.manager.transportDispatcher.jobFinished(1)
        self.manager.transportDispatcher.closeDispatcher()
