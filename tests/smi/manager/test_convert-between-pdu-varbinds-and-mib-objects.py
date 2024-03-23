from pysnmp.smi import builder, view, rfc1902


def test_addAsn1MibSource():
    mibBuilder = builder.MibBuilder()
    mibView = view.MibViewController(mibBuilder)
    mibVar = rfc1902.ObjectIdentity("IF-MIB", "ifInOctets", 1)
    mibVar.addAsn1MibSource("https://mibs.pysnmp.com/asn1/@mib@")
    mibVar.resolveWithMib(mibView)
    assert mibVar.prettyPrint() == "IF-MIB::ifInOctets.1"
