from pysnmp.hlapi import *


def test_v1_set_sync():
    snmpEngine = SnmpEngine()
    errorIndication, errorStatus, errorIndex, varBinds = setCmd(
        snmpEngine,
        CommunityData("public", mpModel=0),
        UdpTransportTarget(("demo.pysnmp.com", 161)),
        ContextData(),
        ObjectType(ObjectIdentity("SNMPv2-MIB", "sysLocation", 0), "Shanghai"),
    )

    assert errorIndication is None
    assert errorStatus == 0
    assert len(varBinds) == 1
    assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysLocation.0"
    assert varBinds[0][1].prettyPrint() == "Shanghai"
    assert isinstance(varBinds[0][1], OctetString)

    snmpEngine.transportDispatcher.closeDispatcher()
