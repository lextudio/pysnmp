#
# This file is part of pysnmp software.
#
# Copyright (c) 2005-2020, Ilya Etingof <etingof@gmail.com>
# License: https://www.pysnmp.com/pysnmp/license.html
#
import time

(MibScalarInstance,) = mibBuilder.import_symbols("SNMPv2-SMI", "MibScalarInstance")

(
    snmpEngineID,
    snmpEngineBoots,
    snmpEngineTime,
    snmpEngineMaxMessageSize,
) = mibBuilder.import_symbols(
    "SNMP-FRAMEWORK-MIB",
    "snmpEngineID",
    "snmpEngineBoots",
    "snmpEngineTime",
    "snmpEngineMaxMessageSize",
)

# snmpEngineTime is Integer32 (0..2147483647) per RFC 3411 §5.3.1. This is only
# the base that _SnmpEngineTime_Type.clone() subtracts from the current time to
# yield the seconds elapsed since this engine booted, so it has to stay inside
# the Integer32 range. The raw Unix time stops fitting on 2038-01-19, at which
# point cloning it raised ValueConstraintError and SnmpEngine() could no longer
# be constructed at all. Keep the base wrapped; the elapsed value it produces
# is correct either way. #205
_SNMP_ENGINE_TIME_MODULUS = 2147483647

__snmpEngineID = MibScalarInstance(snmpEngineID.name, (0,), snmpEngineID.syntax)
__snmpEngineBoots = MibScalarInstance(
    snmpEngineBoots.name, (0,), snmpEngineBoots.syntax.clone(1)
)
__snmpEngineTime = MibScalarInstance(
    snmpEngineTime.name,
    (0,),
    snmpEngineTime.syntax.clone(int(time.time()) % _SNMP_ENGINE_TIME_MODULUS),
)
__snmpEngineMaxMessageSize = MibScalarInstance(
    snmpEngineMaxMessageSize.name, (0,), snmpEngineMaxMessageSize.syntax.clone(4096)
)

mibBuilder.export_symbols(
    "__SNMP-FRAMEWORK-MIB",
    snmpEngineID=__snmpEngineID,
    snmpEngineBoots=__snmpEngineBoots,
    snmpEngineTime=__snmpEngineTime,
    snmpEngineMaxMessageSize=__snmpEngineMaxMessageSize,
)
