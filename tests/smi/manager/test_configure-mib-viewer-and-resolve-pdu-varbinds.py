from pysnmp.smi import builder, view, compiler, rfc1902


def test_configure_mib_viewer_and_resolve_pdu_varbinds():
    # Assemble MIB browser
    mibBuilder = builder.MibBuilder()
    mibViewController = view.MibViewController(mibBuilder)
    compiler.add_mib_compiler(
        mibBuilder,
        sources=["file:///usr/share/snmp/mibs", "https://mibs.pysnmp.com/asn1/@mib@"],
    )

    # Pre-load MIB modules we expect to work with
    mibBuilder.load_modules("SNMPv2-MIB", "SNMP-COMMUNITY-MIB")

    # Check that the MIB browser is correctly configured
    assert isinstance(mibBuilder, builder.MibBuilder)
    assert isinstance(mibViewController, view.MibViewController)

    # Check that the expected MIB modules are loaded
    assert mibBuilder.load_modules("SNMPv2-MIB") is not None
    assert mibBuilder.load_modules("SNMP-COMMUNITY-MIB") is not None

    # Define expected var-binds
    expected_varbinds = [
        "SNMP-COMMUNITY-MIB::snmpTrapCommunity.0 = ",
        "SNMPv2-MIB::snmpTrapEnterprise.0 = SNMPv2-SMI::enterprises.20408.4.1.1.2",
        "SNMPv2-MIB::sysDescr.0 = my system",
    ]

    # This is what we can get in TRAP PDU
    varBinds = [
        ("1.3.6.1.6.3.18.1.4.0", ""),
        ("1.3.6.1.6.3.1.1.4.3.0", "1.3.6.1.4.1.20408.4.1.1.2"),
        ("1.3.6.1.2.1.1.1.0", "my system"),
    ]

    # Run var-binds through MIB resolver
    # You may want to catch and ignore resolution errors here
    varBinds = [
        rfc1902.ObjectType(rfc1902.ObjectIdentity(x[0]), x[1]).resolve_with_mib(
            mibViewController
        )
        for x in varBinds
    ]

    # Check that var-binds were resolved correctly
    for i, varBind in enumerate(varBinds):
        assert isinstance(varBind, rfc1902.ObjectType)
        assert varBind.prettyPrint() == expected_varbinds[i]


def test_configure_mib_viewer_and_resolve_pdu_varbinds_full():
    # Assemble MIB browser
    mibBuilder = builder.MibBuilder()
    mibViewController = view.MibViewController(mibBuilder)
    compiler.add_mib_compiler(
        mibBuilder,
        sources=["file:///usr/share/snmp/mibs", "https://mibs.pysnmp.com/asn1/@mib@"],
    )

    # Pre-load MIB modules we expect to work with
    mibBuilder.load_modules("SNMPv2-MIB", "SNMP-COMMUNITY-MIB", "PYSNMP-MIB")

    # Check that the MIB browser is correctly configured
    assert isinstance(mibBuilder, builder.MibBuilder)
    assert isinstance(mibViewController, view.MibViewController)

    # Check that the expected MIB modules are loaded
    assert mibBuilder.load_modules("SNMPv2-MIB") is not None
    assert mibBuilder.load_modules("SNMP-COMMUNITY-MIB") is not None
    assert mibBuilder.load_modules("PYSNMP-MIB") is not None

    # Define expected var-binds
    expected_varbinds = [
        "SNMP-COMMUNITY-MIB::snmpTrapCommunity.0 = ",
        "SNMPv2-MIB::snmpTrapEnterprise.0 = PYSNMP-MIB::pysnmpNotificationObjects.1.2",
        "SNMPv2-MIB::sysDescr.0 = my system",
    ]

    # This is what we can get in TRAP PDU
    varBinds = [
        ("1.3.6.1.6.3.18.1.4.0", ""),
        ("1.3.6.1.6.3.1.1.4.3.0", "1.3.6.1.4.1.20408.4.1.1.2"),
        ("1.3.6.1.2.1.1.1.0", "my system"),
    ]

    # Run var-binds through MIB resolver
    # You may want to catch and ignore resolution errors here
    varBinds = [
        rfc1902.ObjectType(rfc1902.ObjectIdentity(x[0]), x[1]).resolve_with_mib(
            mibViewController
        )
        for x in varBinds
    ]

    # Check that var-binds were resolved correctly
    for i, varBind in enumerate(varBinds):
        assert isinstance(varBind, rfc1902.ObjectType)
        assert varBind.prettyPrint() == expected_varbinds[i]


def test_syntax_integer():
    # Create MIB builder
    mib_builder = builder.MibBuilder()

    # Load MIB modules
    compiler.addMibCompiler(mib_builder)
    mib_builder.loadModules("LEXTUDIO-TEST-MIB")

    # Get MIB object
    (mib_object,) = mib_builder.import_symbols("LEXTUDIO-TEST-MIB", "testScaledInteger")

    # Print MIB object syntax
    assert (1, 3, 6, 1, 4, 1, 60069, 9, 7) == mib_object.getName()
    assert "ScaledInteger" == mib_object.syntax.__class__.__name__


def test_syntax_unsigned():
    # Create MIB builder
    mib_builder = builder.MibBuilder()

    # Load MIB modules
    compiler.addMibCompiler(mib_builder)
    mib_builder.loadModules("LEXTUDIO-TEST-MIB")

    # Get MIB object
    (mib_object,) = mib_builder.import_symbols(
        "LEXTUDIO-TEST-MIB", "testScaledUnsigned"
    )

    # Print MIB object syntax
    assert (1, 3, 6, 1, 4, 1, 60069, 9, 8) == mib_object.getName()
    assert "ScaledUnsigned" == mib_object.syntax.__class__.__name__
