import pytest
from pysnmp.smi import builder, compiler, view

mibBuilder = builder.MibBuilder()
mibBuilder.loadTexts = True
compiler.addMibCompiler(mibBuilder)
mibView = view.MibViewController(mibBuilder)

mibBuilder.load_modules(
    "SNMPv2-MIB",
    "SNMP-FRAMEWORK-MIB",
    "SNMP-COMMUNITY-MIB",
    "CISCO-ENHANCED-IPSEC-FLOW-MIB",
)


def test_getNodeName_by_OID():
    oid, label, suffix = mibView.get_node_name((1, 3, 6, 1, 2, 1, 1, 1))
    assert oid == (1, 3, 6, 1, 2, 1, 1, 1)
    assert label == (
        "iso",
        "org",
        "dod",
        "internet",
        "mgmt",
        "mib-2",
        "system",
        "sysDescr",
    )
    assert suffix == ()


def test_getNodeName_by_label():
    oid, label, suffix = mibView.get_node_name((1, 3, 6, 1, 2, "mib-2", 1, "sysDescr"))
    assert oid == (1, 3, 6, 1, 2, 1, 1, 1)
    assert label == (
        "iso",
        "org",
        "dod",
        "internet",
        "mgmt",
        "mib-2",
        "system",
        "sysDescr",
    )
    assert suffix == ()


def test_getNodeName_by_symbol_description():
    oid, label, suffix = mibView.get_node_name(("sysDescr",))
    assert oid == (1, 3, 6, 1, 2, 1, 1, 1)
    assert label == (
        "iso",
        "org",
        "dod",
        "internet",
        "mgmt",
        "mib-2",
        "system",
        "sysDescr",
    )
    assert suffix == ()


def test_getNodeName_by_symbol_description_with_module_name():
    oid, label, suffix = mibView.get_node_name(("snmpEngineID",), "SNMP-FRAMEWORK-MIB")
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

    (mibNode,) = mibBuilder.import_symbols("SNMP-FRAMEWORK-MIB", "snmpEngineID")
    assert "" != mibNode.syntax.prettyPrint()


def test_getNodeName_by_symbol_location_lookup_by_name():
    modName, symName, suffix = mibView.get_node_location(("snmpCommunityEntry",))
    assert modName == "SNMP-COMMUNITY-MIB"
    assert symName == "snmpCommunityEntry"
    assert suffix == ()


def test_getNodeName_by_symbol_description_with_module_name_2():
    oid, label, suffix = mibView.get_node_name(
        ("ciscoEnhIPsecFlowActivityGroup",), "CISCO-ENHANCED-IPSEC-FLOW-MIB"
    )
    assert oid == (1, 3, 6, 1, 4, 1, 9, 9, 432, 2, 2, 1)
    assert label == (
        "iso",
        "org",
        "dod",
        "internet",
        "private",
        "enterprises",
        "cisco",
        "ciscoMgmt",
        "ciscoEnhancedIpsecFlowMIB",
        "ciscoEnhancedIpsecFlowMIBConform",
        "ciscoIPsecFlowMIBGroups",
        "ciscoEnhIPsecFlowActivityGroup",
    )
    assert suffix == ()

    (mibNode,) = mibBuilder.import_symbols(
        "CISCO-ENHANCED-IPSEC-FLOW-MIB", "ciscoEnhIPsecFlowActivityGroup"
    )
    assert (
        "This group consists of: 1) IPsec Phase-2 Global Statistics 2) IPsec Phase-2 Tunnel Table 3) IPsec Phase-2 Endpoint Table 4) IPsec Phase-2 Security Association Table"
        == mibNode.getDescription()
    )
    assert "rfc2408, rfc2407; rfc2409 section 5.5" == mibNode.getReference()
