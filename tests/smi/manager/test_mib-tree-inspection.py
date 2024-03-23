import pytest
from pysnmp.smi import builder, compiler, view


mibBuilder = builder.MibBuilder()
mibBuilder.addMibSources(builder.DirMibSource("/opt/pysnmp_mibs"))

# Attach MIB compiler to SNMP Engine (MIB Builder)
# This call will fail if PySMI is not present on the system
compiler.addMibCompiler(mibBuilder)
# ... alternatively, this call will not complain on missing PySMI
# compiler.addMibCompiler(snmpEngine.getMibBuilder(), ifAvailable=True)

mibBuilder.loadModules(
    "SNMPv2-MIB", "SNMP-FRAMEWORK-MIB", "SNMP-COMMUNITY-MIB", "IP-MIB"
)
mibView = view.MibViewController(mibBuilder)


def test_getNodeName_by_OID():
    oid, label, suffix = mibView.getNodeName((1, 3, 6, 1, 2, 1, 1, 1))
    assert oid == (1, 3, 6, 1, 2, 1, 1, 1)
    assert label == (
        "iso",
        "org",
        "dod",
        "internet",
        "snmpV2",
        "snmpModules",
        "system",
        "sysDescr",
    )
    assert suffix == ()


def test_getNodeName_by_label():
    oid, label, suffix = mibView.getNodeName((1, 3, 6, 1, 2, "mib-2", 1, "sysDescr"))
    assert oid == (1, 3, 6, 1, 2, 1, 1, 1)
    assert label == (
        "iso",
        "org",
        "dod",
        "internet",
        "snmpV2",
        "snmpModules",
        "system",
        "sysDescr",
    )
    assert suffix == ()


def test_getNodeName_by_symbol_description():
    oid, label, suffix = mibView.getNodeName(("sysDescr",))
    assert oid == (1, 3, 6, 1, 2, 1, 1, 1)
    assert label == (
        "iso",
        "org",
        "dod",
        "internet",
        "snmpV2",
        "snmpModules",
        "system",
        "sysDescr",
    )
    assert suffix == ()


def test_getNodeName_by_symbol_description_with_module_name():
    oid, label, suffix = mibView.getNodeName(("snmpEngineID",), "SNMP-FRAMEWORK-MIB")
    assert oid == (1, 3, 6, 1, 6, 3, 10, 2, 1, 1)
    assert label == (
        "iso",
        "org",
        "dod",
        "internet",
        "snmpV2",
        "snmpModules",
        "snmpFrameworkMIB",
        "snmpFrameworkMIBObjects",
        "snmpEngine",
        "snmpEngineID",
    )
    assert suffix == ()

    (mibNode,) = mibBuilder.importSymbols("SNMP-FRAMEWORK-MIB", "snmpEngineID")
    assert mibNode.syntax.prettyPrint() != ""


def test_getNodeName_by_symbol_location_lookup_by_name():
    modName, symName, suffix = mibView.getNodeLocation(("snmpCommunityEntry",))
    assert modName == "SNMP-COMMUNITY-MIB"
    assert symName == "snmpCommunityEntry"
    assert suffix == ()
