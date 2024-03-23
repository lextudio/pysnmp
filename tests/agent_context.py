from build.lib.pysnmp.carrier.asyncio.dgram import udp
from pysnmp.carrier.asyncio.dgram import udp6
from pysnmp.entity import config, engine
from pysnmp.entity.rfc3413 import cmdrsp, context
from pysnmp.hlapi.v3arch.asyncio import *


import asyncio
import time

from pysnmp.proto.api import v2c

# Set the port to 1611 instead of 161, because 161 is a
# privileged port and requires root access
AGENT_PORT = 1611


async def start_agent(
    enable_ipv6: bool = False, enable_slow_object: bool = False
) -> SnmpEngine:
    # Create SNMP engine
    snmpEngine = engine.SnmpEngine()

    # Set up transport endpoint
    config.addTransport(
        snmpEngine,
        udp.DOMAIN_NAME,
        udp.UdpTransport().openServerMode(("localhost", AGENT_PORT)),
    )

    if enable_ipv6:
        config.addTransport(
            snmpEngine,
            udp6.DOMAIN_NAME,
            udp6.Udp6Transport().openServerMode(("localhost", AGENT_PORT)),
        )

    # Set up community data
    config.addV1System(snmpEngine, "public", "public")
    # Add SNMP v3 user
    config.addV3User(
        snmpEngine, "usr-none-none", config.USM_AUTH_NONE, config.USM_PRIV_NONE
    )

    config.addV3User(
        snmpEngine,
        "usr-sha-aes",
        config.USM_AUTH_HMAC96_SHA,
        "authkey1",
        config.USM_PRIV_CFB128_AES,
        "privkey1",
    )

    config.addV3User(snmpEngine, "usr-sha-none", config.USM_AUTH_HMAC96_SHA, "authkey1")

    # Allow read MIB access for this user / securityModels at VACM
    config.addVacmUser(snmpEngine, 1, "public", "noAuthNoPriv", (1, 3, 6), (1, 3, 6))
    config.addVacmUser(snmpEngine, 2, "public", "noAuthNoPriv", (1, 3, 6), (1, 3, 6))
    config.addVacmUser(snmpEngine, 3, "usr-none-none", "noAuthNoPriv", (1, 3, 6))
    config.addVacmUser(snmpEngine, 3, "usr-sha-none", "authNoPriv", (1, 3, 6))
    config.addVacmUser(snmpEngine, 3, "usr-sha-aes", "authPriv", (1, 3, 6))

    # Configure SNMP context
    snmpContext = context.SnmpContext(snmpEngine)

    if enable_slow_object:
        # --- create custom Managed Object Instance ---
        mibBuilder = snmpContext.getMibInstrum().getMibBuilder()

        MibScalar, MibScalarInstance = mibBuilder.importSymbols(
            "SNMPv2-SMI", "MibScalar", "MibScalarInstance"
        )

        class MyStaticMibScalarInstance(MibScalarInstance):
            # noinspection PyUnusedLocal,PyUnusedLocal
            def getValue(self, name, idx):
                time.sleep(2)  # Add a 2-second sleep
                return self.getSyntax().clone(f"Test agent")

            def setValue(self, name, idx, value):
                # Here you can handle the SET operation.
                # `value` is the new value for the scalar instance.
                # You should store this value somewhere, and return it in the `getValue` method.
                # For this example, let's just print it.
                print(f"SET operation received. New value: {value}")
                return self.getSyntax().clone(value)

        mibBuilder.exportSymbols(
            "__MY_MIB",
            MibScalar((1, 3, 6, 1, 4, 1, 60069, 9, 1), v2c.OctetString()),
            MyStaticMibScalarInstance(
                (1, 3, 6, 1, 4, 1, 60069, 9, 1), (0,), v2c.OctetString()
            ),
        )

        # --- end of Managed Object Instance initialization ----

    # Register SNMP Applications at the SNMP engine for particular SNMP context
    cmdrsp.GetCommandResponder(snmpEngine, snmpContext)
    cmdrsp.NextCommandResponder(snmpEngine, snmpContext)
    cmdrsp.BulkCommandResponder(snmpEngine, snmpContext)
    cmdrsp.SetCommandResponder(snmpEngine, snmpContext)

    # Start the event loop
    snmpEngine.transportDispatcher.jobStarted(1)

    snmpEngine.transportDispatcher.runDispatcher()

    # Wait for the agent to start
    await asyncio.sleep(1)

    # return the engine
    return snmpEngine


class AgentContextManager:
    """
    A context manager for managing the lifecycle of an SNMP test agent.

    Usage:
    async with AgentContextManager() as agent:
        # Perform operations with the agent

    When the context is entered, the agent is started using the `start_agent()` function.
    When the context is exited, the agent's transport dispatcher is stopped and closed.

    Note: The `start_agent()` function and the `transportDispatcher` attribute are not defined in this code snippet.
    """

    def __init__(self, enable_ipv6: bool = False, enable_slow_object: bool = False):
        self.enable_ipv6 = enable_ipv6
        self.enable_slow_object = enable_slow_object

    async def __aenter__(self):
        self.agent = await start_agent(self.enable_ipv6, self.enable_slow_object)
        return self.agent

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.agent.transportDispatcher.jobFinished(1)
        self.agent.transportDispatcher.closeDispatcher()
