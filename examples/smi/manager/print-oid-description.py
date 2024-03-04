from pysnmp.proto.rfc1902 import ObjectIdentifier
from pysnmp.smi import builder, view, compiler

# Create MIB builder
mibBuilder = builder.MibBuilder()

# Optionally compile MIBs
compiler.addMibCompiler(mibBuilder, sources=["/usr/share/snmp/mibs"])

mibBuilder.loadTexts = True

# Load MIB modules
mibBuilder.loadModules("SNMPv2-MIB")
# mibBuilder.addMibSources(builder.DirMibSource('/Users/lextm/pysnmp.com/pysnmp/mibs'))
# mibBuilder.loadModule('LEXTUDIO-MIB')

# Create MIB view controller
mibViewController = view.MibViewController(mibBuilder)

# Create an OID object
oid = ObjectIdentifier("1.3.6.1.2.1.1.3.0")

# Get the MIB name and symbol name for the OID
modName, symName, suffix = mibViewController.getNodeLocation(oid)

# Get the MIB node for the OID
(mibNode,) = mibBuilder.importSymbols(modName, symName)

# Get the description of the MIB node
description = mibNode.getDescription()

# Print the results
print("OID: %s" % oid)
print("MIB name: %s" % modName)
print("Symbol name: %s" % symName)
print("Description: %s" % description)
print("Syntax: %s" % mibNode.getSyntax().__class__.__name__)
