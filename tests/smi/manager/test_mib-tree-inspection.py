import os
import pytest
from pysnmp.smi import builder, compiler, view

mibBuilder = builder.MibBuilder()
mibBuilder.loadTexts = True
mibBuilder.add_mib_sources(builder.DirMibSource(compiler.DEFAULT_DEST))
mibView = view.MibViewController(mibBuilder)

mibBuilder.load_modules(
    "SNMPv2-MIB",
    "SNMP-FRAMEWORK-MIB",
    "SNMP-COMMUNITY-MIB",
    "CISCO-ENHANCED-IPSEC-FLOW-MIB",
    "PYSNMP-MIB",
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

    # Method 1: Assert that mibNode.syntax is an instance of OctetString
    from pysnmp.proto.rfc1902 import OctetString

    assert isinstance(mibNode.syntax, OctetString), (
        "mibNode.syntax is not an instance of OctetString"
    )

    # Method 2: When you don't know the base class in advance
    # Extract and print the class hierarchy of mibNode.syntax
    syntax_type = type(mibNode.syntax)
    class_hierarchy = []
    for base in syntax_type.__mro__:
        class_hierarchy.append(base.__name__)

    # Check if 'OctetString' is in the class hierarchy
    assert "OctetString" in class_hierarchy, (
        f"OctetString not found in class hierarchy: {class_hierarchy}"
    )

    # Print the class hierarchy for reference
    print(f"Class hierarchy of mibNode.syntax: {class_hierarchy}")

    # Method 3: Find the immediate subclass of SimpleAsn1Type
    from pyasn1.type.base import SimpleAsn1Type

    # Get the full MRO as classes, not just names
    full_mro = syntax_type.__mro__

    # Find SimpleAsn1Type in the MRO
    simple_asn_index = None
    for i, cls in enumerate(full_mro):
        if cls is SimpleAsn1Type:
            simple_asn_index = i
            break

    # If found, the direct subclass is at index - 1, and the subclass above that is at index - 2
    assert simple_asn_index is not None, "SimpleAsn1Type not found in class hierarchy"

    # The class at index - 1 is the immediate subclass of SimpleAsn1Type
    # The class at index - 2 is the subclass above the immediate subclass (i.e., the essential SMI/SNMP data type)
    essential_type = full_mro[simple_asn_index - 2]
    print(f"Essential SMI/SNMP data type: {essential_type.__name__}")

    # Assert that the essential type is OctetString
    assert essential_type is OctetString, (
        f"Essential type is {essential_type.__name__}, not OctetString"
    )


def test_getUnits_by_symbol_description_with_module_name():
    oid, label, suffix = mibView.get_node_name(
        ("snmpEngineTime",), "SNMP-FRAMEWORK-MIB"
    )
    assert oid == (1, 3, 6, 1, 6, 3, 10, 2, 1, 3)
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
        "snmpEngineTime",
    )
    assert suffix == ()

    (mibNode,) = mibBuilder.import_symbols("SNMP-FRAMEWORK-MIB", "snmpEngineTime")
    # assert "" != mibNode.syntax.prettyPrint()

    assert mibNode.getUnits() == "seconds"


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
