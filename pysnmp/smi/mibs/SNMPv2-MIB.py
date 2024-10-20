#
# This file is part of pysnmp software.
#
# Copyright (c) 2005-2020, Ilya Etingof <etingof@gmail.com>
# License: https://www.pysnmp.com/pysnmp/license.html
#
# PySNMP MIB module SNMPv2-MIB (https://www.pysnmp.com/pysnmp)
# ASN.1 source http://mibs.pysnmp.com:80/asn1/SNMPv2-MIB
# Produced by pysmi-0.1.3 at Tue Apr 18 00:52:45 2017
# On host grommit.local platform Darwin version 16.4.0 by user ilya
# Using Python version 3.4.2 (v3.4.2:ab2c023a9432, Oct  5 2014, 20:42:22)
#
OctetString, ObjectIdentifier, Integer = mibBuilder.import_symbols(
    "ASN1", "OctetString", "ObjectIdentifier", "Integer"
)
(NamedValues,) = mibBuilder.import_symbols("ASN1-ENUMERATION", "NamedValues")
(
    SingleValueConstraint,
    ValueSizeConstraint,
    ConstraintsIntersection,
    ValueRangeConstraint,
    ConstraintsUnion,
) = mibBuilder.import_symbols(
    "ASN1-REFINEMENT",
    "SingleValueConstraint",
    "ValueSizeConstraint",
    "ConstraintsIntersection",
    "ValueRangeConstraint",
    "ConstraintsUnion",
)
ObjectGroup, ModuleCompliance, NotificationGroup = mibBuilder.import_symbols(
    "SNMPv2-CONF", "ObjectGroup", "ModuleCompliance", "NotificationGroup"
)
(
    mib_2,
    snmpModules,
    ModuleIdentity,
    Counter64,
    ObjectIdentity,
    Integer32,
    NotificationType,
    iso,
    MibScalar,
    MibTable,
    MibTableRow,
    MibTableColumn,
    Counter32,
    Bits,
    IpAddress,
    Gauge32,
    Unsigned32,
    TimeTicks,
    MibIdentifier,
) = mibBuilder.import_symbols(
    "SNMPv2-SMI",
    "mib-2",
    "snmpModules",
    "ModuleIdentity",
    "Counter64",
    "ObjectIdentity",
    "Integer32",
    "NotificationType",
    "iso",
    "MibScalar",
    "MibTable",
    "MibTableRow",
    "MibTableColumn",
    "Counter32",
    "Bits",
    "IpAddress",
    "Gauge32",
    "Unsigned32",
    "TimeTicks",
    "MibIdentifier",
)
TextualConvention, TestAndIncr, TimeStamp, DisplayString = mibBuilder.import_symbols(
    "SNMPv2-TC", "TextualConvention", "TestAndIncr", "TimeStamp", "DisplayString"
)
snmpMIB = ModuleIdentity((1, 3, 6, 1, 6, 3, 1))
if mibBuilder.loadTexts:
    snmpMIB.setRevisions(
        (
            "2000-08-09 20:17",
            "1995-11-09 00:00",
            "1993-04-01 00:00",
        )
    )
if mibBuilder.loadTexts:
    snmpMIB.setLastUpdated("200008092017Z")
if mibBuilder.loadTexts:
    snmpMIB.setOrganization("IETF SNMPv3 Working Group")
if mibBuilder.loadTexts:
    snmpMIB.setContactInfo(
        "WG-EMail: snmpv3@tis.com Subscribe: majordomo@tis.com In message body: subscribe snmpv3 Chair: Russ Mundy TIS Labs at Network Associates postal: 3060 Washington Rd Glenwood MD 21738 USA EMail: mundy@tislabs.com phone: +1 301 854-6889 Editor: Randy Presuhn BMC Software, Inc. postal: 2141 North First Street San Jose, CA 95131 USA EMail: randy_presuhn@bmc.com phone: +1 408 546-1006"
    )
if mibBuilder.loadTexts:
    snmpMIB.setDescription("The MIB module for SNMP entities.")
snmpMIBObjects = MibIdentifier((1, 3, 6, 1, 6, 3, 1, 1))
system = MibIdentifier((1, 3, 6, 1, 2, 1, 1))
sysDescr = MibScalar(
    (1, 3, 6, 1, 2, 1, 1, 1),
    DisplayString().subtype(subtypeSpec=ValueSizeConstraint(0, 255)),
).setMaxAccess("read-only")
if mibBuilder.loadTexts:
    sysDescr.setStatus("current")
if mibBuilder.loadTexts:
    sysDescr.setDescription(
        "A textual description of the entity. This value should include the full name and version identification of the system's hardware type, software operating-system, and networking software."
    )
sysObjectID = MibScalar((1, 3, 6, 1, 2, 1, 1, 2), ObjectIdentifier()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    sysObjectID.setStatus("current")
if mibBuilder.loadTexts:
    sysObjectID.setDescription(
        "The vendor's authoritative identification of the network management subsystem contained in the entity. This value is allocated within the SMI enterprises subtree (1.3.6.1.4.1) and provides an easy and unambiguous means for determining `what kind of box' is being managed. For example, if vendor `Flintstones, Inc.' was assigned the subtree 1.3.6.1.4.1.424242, it could assign the identifier 1.3.6.1.4.1.424242.1.1 to its `Fred Router'."
    )
sysUpTime = MibScalar((1, 3, 6, 1, 2, 1, 1, 3), TimeTicks()).setMaxAccess("read-only")
if mibBuilder.loadTexts:
    sysUpTime.setStatus("current")
if mibBuilder.loadTexts:
    sysUpTime.setDescription(
        "The time (in hundredths of a second) since the network management portion of the system was last re-initialized."
    )
sysContact = MibScalar(
    (1, 3, 6, 1, 2, 1, 1, 4),
    DisplayString().subtype(subtypeSpec=ValueSizeConstraint(0, 255)),
).setMaxAccess("read-write")
if mibBuilder.loadTexts:
    sysContact.setStatus("current")
if mibBuilder.loadTexts:
    sysContact.setDescription(
        "The textual identification of the contact person for this managed node, together with information on how to contact this person. If no contact information is known, the value is the zero-length string."
    )
sysName = MibScalar(
    (1, 3, 6, 1, 2, 1, 1, 5),
    DisplayString().subtype(subtypeSpec=ValueSizeConstraint(0, 255)),
).setMaxAccess("read-write")
if mibBuilder.loadTexts:
    sysName.setStatus("current")
if mibBuilder.loadTexts:
    sysName.setDescription(
        "An administratively-assigned name for this managed node. By convention, this is the node's fully-qualified domain name. If the name is unknown, the value is the zero-length string."
    )
sysLocation = MibScalar(
    (1, 3, 6, 1, 2, 1, 1, 6),
    DisplayString().subtype(subtypeSpec=ValueSizeConstraint(0, 255)),
).setMaxAccess("read-write")
if mibBuilder.loadTexts:
    sysLocation.setStatus("current")
if mibBuilder.loadTexts:
    sysLocation.setDescription(
        "The physical location of this node (e.g., 'telephone closet, 3rd floor'). If the location is unknown, the value is the zero-length string."
    )
sysServices = MibScalar(
    (1, 3, 6, 1, 2, 1, 1, 7),
    Integer32().subtype(subtypeSpec=ValueRangeConstraint(0, 127)),
).setMaxAccess("read-only")
if mibBuilder.loadTexts:
    sysServices.setStatus("current")
if mibBuilder.loadTexts:
    sysServices.setDescription(
        "A value which indicates the set of services that this entity may potentially offer. The value is a sum. This sum initially takes the value zero. Then, for each layer, L, in the range 1 through 7, that this node performs transactions for, 2 raised to (L - 1) is added to the sum. For example, a node which performs only routing functions would have a value of 4 (2^(3-1)). In contrast, a node which is a host offering application services would have a value of 72 (2^(4-1) + 2^(7-1)). Note that in the context of the Internet suite of protocols, values should be calculated accordingly: layer functionality 1 physical (e.g., repeaters) 2 datalink/subnetwork (e.g., bridges) 3 internet (e.g., supports the IP) 4 end-to-end (e.g., supports the TCP) 7 applications (e.g., supports the SMTP) For systems including OSI protocols, layers 5 and 6 may also be counted."
    )
sysORLastChange = MibScalar((1, 3, 6, 1, 2, 1, 1, 8), TimeStamp()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    sysORLastChange.setStatus("current")
if mibBuilder.loadTexts:
    sysORLastChange.setDescription(
        "The value of sysUpTime at the time of the most recent change in state or value of any instance of sysORID."
    )
sysORTable = MibTable(
    (1, 3, 6, 1, 2, 1, 1, 9),
)
if mibBuilder.loadTexts:
    sysORTable.setStatus("current")
if mibBuilder.loadTexts:
    sysORTable.setDescription(
        "The (conceptual) table listing the capabilities of the local SNMP application acting as a command responder with respect to various MIB modules. SNMP entities having dynamically-configurable support of MIB modules will have a dynamically-varying number of conceptual rows."
    )
sysOREntry = MibTableRow(
    (1, 3, 6, 1, 2, 1, 1, 9, 1),
).setIndexNames((0, "SNMPv2-MIB", "sysORIndex"))
if mibBuilder.loadTexts:
    sysOREntry.setStatus("current")
if mibBuilder.loadTexts:
    sysOREntry.setDescription("An entry (conceptual row) in the sysORTable.")
sysORIndex = MibTableColumn(
    (1, 3, 6, 1, 2, 1, 1, 9, 1, 1),
    Integer32().subtype(subtypeSpec=ValueRangeConstraint(1, 2147483647)),
)
if mibBuilder.loadTexts:
    sysORIndex.setStatus("current")
if mibBuilder.loadTexts:
    sysORIndex.setDescription(
        "The auxiliary variable used for identifying instances of the columnar objects in the sysORTable."
    )
sysORID = MibTableColumn(
    (1, 3, 6, 1, 2, 1, 1, 9, 1, 2), ObjectIdentifier()
).setMaxAccess("read-only")
if mibBuilder.loadTexts:
    sysORID.setStatus("current")
if mibBuilder.loadTexts:
    sysORID.setDescription(
        "An authoritative identification of a capabilities statement with respect to various MIB modules supported by the local SNMP application acting as a command responder."
    )
sysORDescr = MibTableColumn(
    (1, 3, 6, 1, 2, 1, 1, 9, 1, 3), DisplayString()
).setMaxAccess("read-only")
if mibBuilder.loadTexts:
    sysORDescr.setStatus("current")
if mibBuilder.loadTexts:
    sysORDescr.setDescription(
        "A textual description of the capabilities identified by the corresponding instance of sysORID."
    )
sysORUpTime = MibTableColumn((1, 3, 6, 1, 2, 1, 1, 9, 1, 4), TimeStamp()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    sysORUpTime.setStatus("current")
if mibBuilder.loadTexts:
    sysORUpTime.setDescription(
        "The value of sysUpTime at the time this conceptual row was last instantiated."
    )
snmp = MibIdentifier((1, 3, 6, 1, 2, 1, 11))
snmpInPkts = MibScalar((1, 3, 6, 1, 2, 1, 11, 1), Counter32()).setMaxAccess("read-only")
if mibBuilder.loadTexts:
    snmpInPkts.setStatus("current")
if mibBuilder.loadTexts:
    snmpInPkts.setDescription(
        "The total number of messages delivered to the SNMP entity from the transport service."
    )
snmpInBadVersions = MibScalar((1, 3, 6, 1, 2, 1, 11, 3), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    snmpInBadVersions.setStatus("current")
if mibBuilder.loadTexts:
    snmpInBadVersions.setDescription(
        "The total number of SNMP messages which were delivered to the SNMP entity and were for an unsupported SNMP version."
    )
snmpInBadCommunityNames = MibScalar(
    (1, 3, 6, 1, 2, 1, 11, 4), Counter32()
).setMaxAccess("read-only")
if mibBuilder.loadTexts:
    snmpInBadCommunityNames.setStatus("current")
if mibBuilder.loadTexts:
    snmpInBadCommunityNames.setDescription(
        "The total number of community-based SNMP messages (for example, SNMPv1) delivered to the SNMP entity which used an SNMP community name not known to said entity. Also, implementations which authenticate community-based SNMP messages using check(s) in addition to matching the community name (for example, by also checking whether the message originated from a transport address allowed to use a specified community name) MAY include in this value the number of messages which failed the additional check(s). It is strongly RECOMMENDED that the documentation for any security model which is used to authenticate community-based SNMP messages specify the precise conditions that contribute to this value."
    )
snmpInBadCommunityUses = MibScalar((1, 3, 6, 1, 2, 1, 11, 5), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    snmpInBadCommunityUses.setStatus("current")
if mibBuilder.loadTexts:
    snmpInBadCommunityUses.setDescription(
        "The total number of community-based SNMP messages (for example, SNMPv1) delivered to the SNMP entity which represented an SNMP operation that was not allowed for the SNMP community named in the message. The precise conditions under which this counter is incremented (if at all) depend on how the SNMP entity implements its access control mechanism and how its applications interact with that access control mechanism. It is strongly RECOMMENDED that the documentation for any access control mechanism which is used to control access to and visibility of MIB instrumentation specify the precise conditions that contribute to this value."
    )
snmpInASNParseErrs = MibScalar((1, 3, 6, 1, 2, 1, 11, 6), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    snmpInASNParseErrs.setStatus("current")
if mibBuilder.loadTexts:
    snmpInASNParseErrs.setDescription(
        "The total number of ASN.1 or BER errors encountered by the SNMP entity when decoding received SNMP messages."
    )
snmpEnableAuthenTraps = MibScalar(
    (1, 3, 6, 1, 2, 1, 11, 30),
    Integer32()
    .subtype(subtypeSpec=ConstraintsUnion(SingleValueConstraint(1, 2)))
    .clone(namedValues=NamedValues(("enabled", 1), ("disabled", 2))),
).setMaxAccess("read-write")
if mibBuilder.loadTexts:
    snmpEnableAuthenTraps.setStatus("current")
if mibBuilder.loadTexts:
    snmpEnableAuthenTraps.setDescription(
        "Indicates whether the SNMP entity is permitted to generate authenticationFailure traps. The value of this object overrides any configuration information; as such, it provides a means whereby all authenticationFailure traps may be disabled. Note that it is strongly recommended that this object be stored in non-volatile memory so that it remains constant across re-initializations of the network management system."
    )
snmpSilentDrops = MibScalar((1, 3, 6, 1, 2, 1, 11, 31), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    snmpSilentDrops.setStatus("current")
if mibBuilder.loadTexts:
    snmpSilentDrops.setDescription(
        "The total number of Confirmed Class PDUs (such as GetRequest-PDUs, GetNextRequest-PDUs, GetBulkRequest-PDUs, SetRequest-PDUs, and InformRequest-PDUs) delivered to the SNMP entity which were silently dropped because the size of a reply containing an alternate Response Class PDU (such as a Response-PDU) with an empty variable-bindings field was greater than either a local constraint or the maximum message size associated with the originator of the request."
    )
snmpProxyDrops = MibScalar((1, 3, 6, 1, 2, 1, 11, 32), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    snmpProxyDrops.setStatus("current")
if mibBuilder.loadTexts:
    snmpProxyDrops.setDescription(
        "The total number of Confirmed Class PDUs (such as GetRequest-PDUs, GetNextRequest-PDUs, GetBulkRequest-PDUs, SetRequest-PDUs, and InformRequest-PDUs) delivered to the SNMP entity which were silently dropped because the transmission of the (possibly translated) message to a proxy target failed in a manner (other than a time-out) such that no Response Class PDU (such as a Response-PDU) could be returned."
    )
snmpTrap = MibIdentifier((1, 3, 6, 1, 6, 3, 1, 1, 4))
snmpTrapOID = MibScalar(
    (1, 3, 6, 1, 6, 3, 1, 1, 4, 1), ObjectIdentifier()
).setMaxAccess("accessible-for-notify")
if mibBuilder.loadTexts:
    snmpTrapOID.setStatus("current")
if mibBuilder.loadTexts:
    snmpTrapOID.setDescription(
        "The authoritative identification of the notification currently being sent. This variable occurs as the second varbind in every SNMPv2-Trap-PDU and InformRequest-PDU."
    )
snmpTrapEnterprise = MibScalar(
    (1, 3, 6, 1, 6, 3, 1, 1, 4, 3), ObjectIdentifier()
).setMaxAccess("accessible-for-notify")
if mibBuilder.loadTexts:
    snmpTrapEnterprise.setStatus("current")
if mibBuilder.loadTexts:
    snmpTrapEnterprise.setDescription(
        "The authoritative identification of the enterprise associated with the trap currently being sent. When an SNMP proxy agent is mapping an RFC1157 Trap-PDU into a SNMPv2-Trap-PDU, this variable occurs as the last varbind."
    )
snmpTraps = MibIdentifier((1, 3, 6, 1, 6, 3, 1, 1, 5))
coldStart = NotificationType((1, 3, 6, 1, 6, 3, 1, 1, 5, 1)).setObjects()
if mibBuilder.loadTexts:
    coldStart.setStatus("current")
if mibBuilder.loadTexts:
    coldStart.setDescription(
        "A coldStart trap signifies that the SNMP entity, supporting a notification originator application, is reinitializing itself and that its configuration may have been altered."
    )
warmStart = NotificationType((1, 3, 6, 1, 6, 3, 1, 1, 5, 2)).setObjects()
if mibBuilder.loadTexts:
    warmStart.setStatus("current")
if mibBuilder.loadTexts:
    warmStart.setDescription(
        "A warmStart trap signifies that the SNMP entity, supporting a notification originator application, is reinitializing itself such that its configuration is unaltered."
    )
authenticationFailure = NotificationType((1, 3, 6, 1, 6, 3, 1, 1, 5, 5)).setObjects()
if mibBuilder.loadTexts:
    authenticationFailure.setStatus("current")
if mibBuilder.loadTexts:
    authenticationFailure.setDescription(
        "An authenticationFailure trap signifies that the SNMP entity has received a protocol message that is not properly authenticated. While all implementations of SNMP entities MAY be capable of generating this trap, the snmpEnableAuthenTraps object indicates whether this trap will be generated."
    )
snmpSet = MibIdentifier((1, 3, 6, 1, 6, 3, 1, 1, 6))
snmpSetSerialNo = MibScalar((1, 3, 6, 1, 6, 3, 1, 1, 6, 1), TestAndIncr()).setMaxAccess(
    "read-write"
)
if mibBuilder.loadTexts:
    snmpSetSerialNo.setStatus("current")
if mibBuilder.loadTexts:
    snmpSetSerialNo.setDescription(
        "An advisory lock used to allow several cooperating command generator applications to coordinate their use of the SNMP set operation. This object is used for coarse-grain coordination. To achieve fine-grain coordination, one or more similar objects might be defined within each MIB group, as appropriate."
    )
snmpMIBConformance = MibIdentifier((1, 3, 6, 1, 6, 3, 1, 2))
snmpMIBCompliances = MibIdentifier((1, 3, 6, 1, 6, 3, 1, 2, 1))
snmpMIBGroups = MibIdentifier((1, 3, 6, 1, 6, 3, 1, 2, 2))
snmpBasicCompliance = ModuleCompliance((1, 3, 6, 1, 6, 3, 1, 2, 1, 2)).setObjects(
    ("SNMPv2-MIB", "snmpGroup"),
    ("SNMPv2-MIB", "snmpSetGroup"),
    ("SNMPv2-MIB", "systemGroup"),
    ("SNMPv2-MIB", "snmpBasicNotificationsGroup"),
    ("SNMPv2-MIB", "snmpCommunityGroup"),
)
if mibBuilder.loadTexts:
    snmpBasicCompliance.setDescription(
        "The compliance statement for SNMPv2 entities which implement the SNMPv2 MIB. This compliance statement is replaced by snmpBasicComplianceRev2."
    )
snmpBasicComplianceRev2 = ModuleCompliance((1, 3, 6, 1, 6, 3, 1, 2, 1, 3)).setObjects(
    ("SNMPv2-MIB", "snmpGroup"),
    ("SNMPv2-MIB", "snmpSetGroup"),
    ("SNMPv2-MIB", "systemGroup"),
    ("SNMPv2-MIB", "snmpBasicNotificationsGroup"),
    ("SNMPv2-MIB", "snmpCommunityGroup"),
    ("SNMPv2-MIB", "snmpWarmStartNotificationGroup"),
)
if mibBuilder.loadTexts:
    snmpBasicComplianceRev2.setDescription(
        "The compliance statement for SNMP entities which implement this MIB module."
    )
snmpGroup = ObjectGroup((1, 3, 6, 1, 6, 3, 1, 2, 2, 8)).setObjects(
    ("SNMPv2-MIB", "snmpInPkts"),
    ("SNMPv2-MIB", "snmpInBadVersions"),
    ("SNMPv2-MIB", "snmpInASNParseErrs"),
    ("SNMPv2-MIB", "snmpSilentDrops"),
    ("SNMPv2-MIB", "snmpProxyDrops"),
    ("SNMPv2-MIB", "snmpEnableAuthenTraps"),
)
if mibBuilder.loadTexts:
    snmpGroup.setDescription(
        "A collection of objects providing basic instrumentation and control of an SNMP entity."
    )
snmpCommunityGroup = ObjectGroup((1, 3, 6, 1, 6, 3, 1, 2, 2, 9)).setObjects(
    ("SNMPv2-MIB", "snmpInBadCommunityNames"), ("SNMPv2-MIB", "snmpInBadCommunityUses")
)
if mibBuilder.loadTexts:
    snmpCommunityGroup.setDescription(
        "A collection of objects providing basic instrumentation of a SNMP entity which supports community-based authentication."
    )
snmpSetGroup = ObjectGroup((1, 3, 6, 1, 6, 3, 1, 2, 2, 5)).setObjects(
    ("SNMPv2-MIB", "snmpSetSerialNo")
)
if mibBuilder.loadTexts:
    snmpSetGroup.setDescription(
        "A collection of objects which allow several cooperating command generator applications to coordinate their use of the set operation."
    )
systemGroup = ObjectGroup((1, 3, 6, 1, 6, 3, 1, 2, 2, 6)).setObjects(
    ("SNMPv2-MIB", "sysDescr"),
    ("SNMPv2-MIB", "sysObjectID"),
    ("SNMPv2-MIB", "sysUpTime"),
    ("SNMPv2-MIB", "sysContact"),
    ("SNMPv2-MIB", "sysName"),
    ("SNMPv2-MIB", "sysLocation"),
    ("SNMPv2-MIB", "sysServices"),
    ("SNMPv2-MIB", "sysORLastChange"),
    ("SNMPv2-MIB", "sysORID"),
    ("SNMPv2-MIB", "sysORUpTime"),
    ("SNMPv2-MIB", "sysORDescr"),
)
if mibBuilder.loadTexts:
    systemGroup.setDescription(
        "The system group defines objects which are common to all managed systems."
    )
snmpBasicNotificationsGroup = NotificationGroup(
    (1, 3, 6, 1, 6, 3, 1, 2, 2, 7)
).setObjects(("SNMPv2-MIB", "coldStart"), ("SNMPv2-MIB", "authenticationFailure"))
if mibBuilder.loadTexts:
    snmpBasicNotificationsGroup.setDescription(
        "The basic notifications implemented by an SNMP entity supporting command responder applications."
    )
snmpWarmStartNotificationGroup = NotificationGroup(
    (1, 3, 6, 1, 6, 3, 1, 2, 2, 11)
).setObjects(("SNMPv2-MIB", "warmStart"))
if mibBuilder.loadTexts:
    snmpWarmStartNotificationGroup.setDescription(
        "An additional notification for an SNMP entity supporting command responder applications, if it is able to reinitialize itself such that its configuration is unaltered."
    )
snmpNotificationGroup = ObjectGroup((1, 3, 6, 1, 6, 3, 1, 2, 2, 12)).setObjects(
    ("SNMPv2-MIB", "snmpTrapOID"), ("SNMPv2-MIB", "snmpTrapEnterprise")
)
if mibBuilder.loadTexts:
    snmpNotificationGroup.setDescription(
        "These objects are required for entities which support notification originator applications."
    )
snmpOutPkts = MibScalar((1, 3, 6, 1, 2, 1, 11, 2), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    snmpOutPkts.setStatus("obsolete")
if mibBuilder.loadTexts:
    snmpOutPkts.setDescription(
        "The total number of SNMP Messages which were passed from the SNMP protocol entity to the transport service."
    )
snmpInTooBigs = MibScalar((1, 3, 6, 1, 2, 1, 11, 8), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    snmpInTooBigs.setStatus("obsolete")
if mibBuilder.loadTexts:
    snmpInTooBigs.setDescription(
        "The total number of SNMP PDUs which were delivered to the SNMP protocol entity and for which the value of the error-status field was `tooBig'."
    )
snmpInNoSuchNames = MibScalar((1, 3, 6, 1, 2, 1, 11, 9), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    snmpInNoSuchNames.setStatus("obsolete")
if mibBuilder.loadTexts:
    snmpInNoSuchNames.setDescription(
        "The total number of SNMP PDUs which were delivered to the SNMP protocol entity and for which the value of the error-status field was `noSuchName'."
    )
snmpInBadValues = MibScalar((1, 3, 6, 1, 2, 1, 11, 10), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    snmpInBadValues.setStatus("obsolete")
if mibBuilder.loadTexts:
    snmpInBadValues.setDescription(
        "The total number of SNMP PDUs which were delivered to the SNMP protocol entity and for which the value of the error-status field was `badValue'."
    )
snmpInReadOnlys = MibScalar((1, 3, 6, 1, 2, 1, 11, 11), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    snmpInReadOnlys.setStatus("obsolete")
if mibBuilder.loadTexts:
    snmpInReadOnlys.setDescription(
        "The total number valid SNMP PDUs which were delivered to the SNMP protocol entity and for which the value of the error-status field was `readOnly'. It should be noted that it is a protocol error to generate an SNMP PDU which contains the value `readOnly' in the error-status field, as such this object is provided as a means of detecting incorrect implementations of the SNMP."
    )
snmpInGenErrs = MibScalar((1, 3, 6, 1, 2, 1, 11, 12), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    snmpInGenErrs.setStatus("obsolete")
if mibBuilder.loadTexts:
    snmpInGenErrs.setDescription(
        "The total number of SNMP PDUs which were delivered to the SNMP protocol entity and for which the value of the error-status field was `genErr'."
    )
snmpInTotalReqVars = MibScalar((1, 3, 6, 1, 2, 1, 11, 13), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    snmpInTotalReqVars.setStatus("obsolete")
if mibBuilder.loadTexts:
    snmpInTotalReqVars.setDescription(
        "The total number of MIB objects which have been retrieved successfully by the SNMP protocol entity as the result of receiving valid SNMP Get-Request and Get-Next PDUs."
    )
snmpInTotalSetVars = MibScalar((1, 3, 6, 1, 2, 1, 11, 14), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    snmpInTotalSetVars.setStatus("obsolete")
if mibBuilder.loadTexts:
    snmpInTotalSetVars.setDescription(
        "The total number of MIB objects which have been altered successfully by the SNMP protocol entity as the result of receiving valid SNMP Set-Request PDUs."
    )
snmpInGetRequests = MibScalar((1, 3, 6, 1, 2, 1, 11, 15), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    snmpInGetRequests.setStatus("obsolete")
if mibBuilder.loadTexts:
    snmpInGetRequests.setDescription(
        "The total number of SNMP Get-Request PDUs which have been accepted and processed by the SNMP protocol entity."
    )
snmpInGetNexts = MibScalar((1, 3, 6, 1, 2, 1, 11, 16), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    snmpInGetNexts.setStatus("obsolete")
if mibBuilder.loadTexts:
    snmpInGetNexts.setDescription(
        "The total number of SNMP Get-Next PDUs which have been accepted and processed by the SNMP protocol entity."
    )
snmpInSetRequests = MibScalar((1, 3, 6, 1, 2, 1, 11, 17), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    snmpInSetRequests.setStatus("obsolete")
if mibBuilder.loadTexts:
    snmpInSetRequests.setDescription(
        "The total number of SNMP Set-Request PDUs which have been accepted and processed by the SNMP protocol entity."
    )
snmpInGetResponses = MibScalar((1, 3, 6, 1, 2, 1, 11, 18), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    snmpInGetResponses.setStatus("obsolete")
if mibBuilder.loadTexts:
    snmpInGetResponses.setDescription(
        "The total number of SNMP Get-Response PDUs which have been accepted and processed by the SNMP protocol entity."
    )
snmpInTraps = MibScalar((1, 3, 6, 1, 2, 1, 11, 19), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    snmpInTraps.setStatus("obsolete")
if mibBuilder.loadTexts:
    snmpInTraps.setDescription(
        "The total number of SNMP Trap PDUs which have been accepted and processed by the SNMP protocol entity."
    )
snmpOutTooBigs = MibScalar((1, 3, 6, 1, 2, 1, 11, 20), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    snmpOutTooBigs.setStatus("obsolete")
if mibBuilder.loadTexts:
    snmpOutTooBigs.setDescription(
        "The total number of SNMP PDUs which were generated by the SNMP protocol entity and for which the value of the error-status field was `tooBig.'"
    )
snmpOutNoSuchNames = MibScalar((1, 3, 6, 1, 2, 1, 11, 21), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    snmpOutNoSuchNames.setStatus("obsolete")
if mibBuilder.loadTexts:
    snmpOutNoSuchNames.setDescription(
        "The total number of SNMP PDUs which were generated by the SNMP protocol entity and for which the value of the error-status was `noSuchName'."
    )
snmpOutBadValues = MibScalar((1, 3, 6, 1, 2, 1, 11, 22), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    snmpOutBadValues.setStatus("obsolete")
if mibBuilder.loadTexts:
    snmpOutBadValues.setDescription(
        "The total number of SNMP PDUs which were generated by the SNMP protocol entity and for which the value of the error-status field was `badValue'."
    )
snmpOutGenErrs = MibScalar((1, 3, 6, 1, 2, 1, 11, 24), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    snmpOutGenErrs.setStatus("obsolete")
if mibBuilder.loadTexts:
    snmpOutGenErrs.setDescription(
        "The total number of SNMP PDUs which were generated by the SNMP protocol entity and for which the value of the error-status field was `genErr'."
    )
snmpOutGetRequests = MibScalar((1, 3, 6, 1, 2, 1, 11, 25), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    snmpOutGetRequests.setStatus("obsolete")
if mibBuilder.loadTexts:
    snmpOutGetRequests.setDescription(
        "The total number of SNMP Get-Request PDUs which have been generated by the SNMP protocol entity."
    )
snmpOutGetNexts = MibScalar((1, 3, 6, 1, 2, 1, 11, 26), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    snmpOutGetNexts.setStatus("obsolete")
if mibBuilder.loadTexts:
    snmpOutGetNexts.setDescription(
        "The total number of SNMP Get-Next PDUs which have been generated by the SNMP protocol entity."
    )
snmpOutSetRequests = MibScalar((1, 3, 6, 1, 2, 1, 11, 27), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    snmpOutSetRequests.setStatus("obsolete")
if mibBuilder.loadTexts:
    snmpOutSetRequests.setDescription(
        "The total number of SNMP Set-Request PDUs which have been generated by the SNMP protocol entity."
    )
snmpOutGetResponses = MibScalar((1, 3, 6, 1, 2, 1, 11, 28), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    snmpOutGetResponses.setStatus("obsolete")
if mibBuilder.loadTexts:
    snmpOutGetResponses.setDescription(
        "The total number of SNMP Get-Response PDUs which have been generated by the SNMP protocol entity."
    )
snmpOutTraps = MibScalar((1, 3, 6, 1, 2, 1, 11, 29), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    snmpOutTraps.setStatus("obsolete")
if mibBuilder.loadTexts:
    snmpOutTraps.setDescription(
        "The total number of SNMP Trap PDUs which have been generated by the SNMP protocol entity."
    )
snmpObsoleteGroup = ObjectGroup((1, 3, 6, 1, 6, 3, 1, 2, 2, 10)).setObjects(
    ("SNMPv2-MIB", "snmpOutPkts"),
    ("SNMPv2-MIB", "snmpInTooBigs"),
    ("SNMPv2-MIB", "snmpInNoSuchNames"),
    ("SNMPv2-MIB", "snmpInBadValues"),
    ("SNMPv2-MIB", "snmpInReadOnlys"),
    ("SNMPv2-MIB", "snmpInGenErrs"),
    ("SNMPv2-MIB", "snmpInTotalReqVars"),
    ("SNMPv2-MIB", "snmpInTotalSetVars"),
    ("SNMPv2-MIB", "snmpInGetRequests"),
    ("SNMPv2-MIB", "snmpInGetNexts"),
    ("SNMPv2-MIB", "snmpInSetRequests"),
    ("SNMPv2-MIB", "snmpInGetResponses"),
    ("SNMPv2-MIB", "snmpInTraps"),
    ("SNMPv2-MIB", "snmpOutTooBigs"),
    ("SNMPv2-MIB", "snmpOutNoSuchNames"),
    ("SNMPv2-MIB", "snmpOutBadValues"),
    ("SNMPv2-MIB", "snmpOutGenErrs"),
    ("SNMPv2-MIB", "snmpOutGetRequests"),
    ("SNMPv2-MIB", "snmpOutGetNexts"),
    ("SNMPv2-MIB", "snmpOutSetRequests"),
    ("SNMPv2-MIB", "snmpOutGetResponses"),
    ("SNMPv2-MIB", "snmpOutTraps"),
)
if mibBuilder.loadTexts:
    snmpObsoleteGroup.setDescription(
        "A collection of objects from RFC 1213 made obsolete by this MIB module."
    )
mibBuilder.export_symbols(
    "SNMPv2-MIB",
    snmpOutBadValues=snmpOutBadValues,
    coldStart=coldStart,
    snmpOutPkts=snmpOutPkts,
    snmpSilentDrops=snmpSilentDrops,
    snmpCommunityGroup=snmpCommunityGroup,
    sysORLastChange=sysORLastChange,
    sysName=sysName,
    snmpBasicNotificationsGroup=snmpBasicNotificationsGroup,
    systemGroup=systemGroup,
    snmpInNoSuchNames=snmpInNoSuchNames,
    snmpInTotalSetVars=snmpInTotalSetVars,
    snmpOutTooBigs=snmpOutTooBigs,
    snmpInBadCommunityNames=snmpInBadCommunityNames,
    snmpInASNParseErrs=snmpInASNParseErrs,
    snmpProxyDrops=snmpProxyDrops,
    snmpInPkts=snmpInPkts,
    snmpInSetRequests=snmpInSetRequests,
    snmpInTraps=snmpInTraps,
    sysORIndex=sysORIndex,
    snmpOutGetRequests=snmpOutGetRequests,
    PYSNMP_MODULE_ID=snmpMIB,
    snmpMIB=snmpMIB,
    snmpTrap=snmpTrap,
    sysOREntry=sysOREntry,
    snmp=snmp,
    snmpSet=snmpSet,
    warmStart=warmStart,
    snmpOutGetNexts=snmpOutGetNexts,
    snmpOutGetResponses=snmpOutGetResponses,
    snmpGroup=snmpGroup,
    sysLocation=sysLocation,
    snmpOutSetRequests=snmpOutSetRequests,
    snmpMIBGroups=snmpMIBGroups,
    snmpTrapOID=snmpTrapOID,
    system=system,
    snmpWarmStartNotificationGroup=snmpWarmStartNotificationGroup,
    snmpInBadCommunityUses=snmpInBadCommunityUses,
    snmpBasicComplianceRev2=snmpBasicComplianceRev2,
    sysContact=sysContact,
    snmpInGetNexts=snmpInGetNexts,
    sysORUpTime=sysORUpTime,
    snmpInGetResponses=snmpInGetResponses,
    snmpTraps=snmpTraps,
    snmpInGenErrs=snmpInGenErrs,
    snmpInReadOnlys=snmpInReadOnlys,
    snmpMIBCompliances=snmpMIBCompliances,
    snmpMIBObjects=snmpMIBObjects,
    snmpOutTraps=snmpOutTraps,
    snmpEnableAuthenTraps=snmpEnableAuthenTraps,
    snmpSetSerialNo=snmpSetSerialNo,
    snmpInTotalReqVars=snmpInTotalReqVars,
    snmpInBadVersions=snmpInBadVersions,
    snmpMIBConformance=snmpMIBConformance,
    sysORTable=sysORTable,
    sysORID=sysORID,
    snmpInTooBigs=snmpInTooBigs,
    sysORDescr=sysORDescr,
    sysUpTime=sysUpTime,
    sysDescr=sysDescr,
    snmpBasicCompliance=snmpBasicCompliance,
    snmpInGetRequests=snmpInGetRequests,
    snmpInBadValues=snmpInBadValues,
    snmpSetGroup=snmpSetGroup,
    sysServices=sysServices,
    snmpOutNoSuchNames=snmpOutNoSuchNames,
    sysObjectID=sysObjectID,
    authenticationFailure=authenticationFailure,
    snmpObsoleteGroup=snmpObsoleteGroup,
    snmpOutGenErrs=snmpOutGenErrs,
    snmpTrapEnterprise=snmpTrapEnterprise,
    snmpNotificationGroup=snmpNotificationGroup,
)
