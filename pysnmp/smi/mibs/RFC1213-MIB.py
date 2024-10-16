#
# This file is part of pysnmp software.
#
# Copyright (c) 2005-2020, Ilya Etingof <etingof@gmail.com>
# License: https://www.pysnmp.com/pysnmp/license.html
#
# PySNMP MIB module RFC1213-MIB (https://www.pysnmp.com/pysnmp)
# ASN.1 source http://mibs.pysnmp.com:80/asn1/RFC1213-MIB
# Produced by pysmi-0.1.3 at Mon Apr 17 12:12:07 2017
# On host grommit.local platform Darwin version 16.4.0 by user ilya
# Using Python version 3.4.2 (v3.4.2:ab2c023a9432, Oct  5 2014, 20:42:22)
#
# It is a stripped version of MIB that contains only symbols that is
# unique to SMIv1 and have no analogues in SMIv2
#
from pysnmp.proto.rfc1155 import NetworkAddress

OctetString, ObjectIdentifier, Integer = mibBuilder.import_symbols(
    "ASN1", "OctetString", "ObjectIdentifier", "Integer"
)
(NamedValues,) = mibBuilder.import_symbols("ASN1-ENUMERATION", "NamedValues")
(
    SingleValueConstraint,
    ConstraintsIntersection,
    ValueSizeConstraint,
    ConstraintsUnion,
    ValueRangeConstraint,
) = mibBuilder.import_symbols(
    "ASN1-REFINEMENT",
    "SingleValueConstraint",
    "ConstraintsIntersection",
    "ValueSizeConstraint",
    "ConstraintsUnion",
    "ValueRangeConstraint",
)
ModuleCompliance, NotificationGroup = mibBuilder.import_symbols(
    "SNMPv2-CONF", "ModuleCompliance", "NotificationGroup"
)
(
    IpAddress,
    TimeTicks,
    NotificationType,
    ModuleIdentity,
    Integer32,
    Counter32,
    MibIdentifier,
    ObjectIdentity,
    Gauge32,
    Unsigned32,
    mgmt,
    MibScalar,
    MibTable,
    MibTableRow,
    MibTableColumn,
    Bits,
    iso,
    Counter64,
    mib_2,
) = mibBuilder.import_symbols(
    "SNMPv2-SMI",
    "IpAddress",
    "TimeTicks",
    "NotificationType",
    "ModuleIdentity",
    "Integer32",
    "Counter32",
    "MibIdentifier",
    "ObjectIdentity",
    "Gauge32",
    "Unsigned32",
    "mgmt",
    "MibScalar",
    "MibTable",
    "MibTableRow",
    "MibTableColumn",
    "Bits",
    "iso",
    "Counter64",
    "mib-2",
)
DisplayString, PhysAddress = mibBuilder.import_symbols(
    "SNMPv2-TC", "DisplayString", "PhysAddress"
)


at = MibIdentifier((1, 3, 6, 1, 2, 1, 3))
ip = MibIdentifier((1, 3, 6, 1, 2, 1, 4))
egp = MibIdentifier((1, 3, 6, 1, 2, 1, 8))
atTable = MibTable(
    (1, 3, 6, 1, 2, 1, 3, 1),
)
if mibBuilder.loadTexts:
    atTable.setStatus("deprecated")
if mibBuilder.loadTexts:
    atTable.setDescription(
        "The Address Translation tables contain the NetworkAddress to `physical' address equivalences. Some interfaces do not use translation tables for determining address equivalences (e.g., DDN-X.25 has an algorithmic method); if all interfaces are of this type, then the Address Translation table is empty, i.e., has zero entries."
    )
atEntry = MibTableRow(
    (1, 3, 6, 1, 2, 1, 3, 1, 1),
).setIndexNames((0, "RFC1213-MIB", "atIfIndex"), (0, "RFC1213-MIB", "atNetAddress"))
if mibBuilder.loadTexts:
    atEntry.setStatus("deprecated")
if mibBuilder.loadTexts:
    atEntry.setDescription(
        "Each entry contains one NetworkAddress to `physical' address equivalence."
    )
atIfIndex = MibTableColumn((1, 3, 6, 1, 2, 1, 3, 1, 1, 1), Integer32()).setMaxAccess(
    "read-write"
)
if mibBuilder.loadTexts:
    atIfIndex.setStatus("deprecated")
if mibBuilder.loadTexts:
    atIfIndex.setDescription(
        "The interface on which this entry's equivalence is effective. The interface identified by a particular value of this index is the same interface as identified by the same value of ifIndex."
    )
atPhysAddress = MibTableColumn(
    (1, 3, 6, 1, 2, 1, 3, 1, 1, 2), PhysAddress()
).setMaxAccess("read-write")
if mibBuilder.loadTexts:
    atPhysAddress.setStatus("deprecated")
if mibBuilder.loadTexts:
    atPhysAddress.setDescription(
        "The media-dependent `physical' address. Setting this object to a null string (one of zero length) has the effect of invaliding the corresponding entry in the atTable object. That is, it effectively dissasociates the interface identified with said entry from the mapping identified with said entry. It is an implementation-specific matter as to whether the agent removes an invalidated entry from the table. Accordingly, management stations must be prepared to receive tabular information from agents that corresponds to entries not currently in use. Proper interpretation of such entries requires examination of the relevant atPhysAddress object."
    )
atNetAddress = MibTableColumn(
    (1, 3, 6, 1, 2, 1, 3, 1, 1, 3), NetworkAddress()
).setMaxAccess("read-write")
if mibBuilder.loadTexts:
    atNetAddress.setStatus("deprecated")
if mibBuilder.loadTexts:
    atNetAddress.setDescription(
        "The NetworkAddress (e.g., the IP address) corresponding to the media-dependent `physical' address."
    )
ipForwarding = MibScalar(
    (1, 3, 6, 1, 2, 1, 4, 1),
    Integer32()
    .subtype(subtypeSpec=ConstraintsUnion(SingleValueConstraint(1, 2)))
    .clone(namedValues=NamedValues(("forwarding", 1), ("not-forwarding", 2))),
).setMaxAccess("read-write")
if mibBuilder.loadTexts:
    ipForwarding.setStatus("mandatory")
if mibBuilder.loadTexts:
    ipForwarding.setDescription(
        "The indication of whether this entity is acting as an IP gateway in respect to the forwarding of datagrams received by, but not addressed to, this entity. IP gateways forward datagrams. IP hosts do not (except those source-routed via the host). Note that for some managed nodes, this object may take on only a subset of the values possible. Accordingly, it is appropriate for an agent to return a `badValue' response if a management station attempts to change this object to an inappropriate value."
    )
ipDefaultTTL = MibScalar((1, 3, 6, 1, 2, 1, 4, 2), Integer32()).setMaxAccess(
    "read-write"
)
if mibBuilder.loadTexts:
    ipDefaultTTL.setStatus("mandatory")
if mibBuilder.loadTexts:
    ipDefaultTTL.setDescription(
        "The default value inserted into the Time-To-Live field of the IP header of datagrams originated at this entity, whenever a TTL value is not supplied by the transport layer protocol."
    )
ipInReceives = MibScalar((1, 3, 6, 1, 2, 1, 4, 3), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    ipInReceives.setStatus("mandatory")
if mibBuilder.loadTexts:
    ipInReceives.setDescription(
        "The total number of input datagrams received from interfaces, including those received in error."
    )
ipInHdrErrors = MibScalar((1, 3, 6, 1, 2, 1, 4, 4), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    ipInHdrErrors.setStatus("mandatory")
if mibBuilder.loadTexts:
    ipInHdrErrors.setDescription(
        "The number of input datagrams discarded due to errors in their IP headers, including bad checksums, version number mismatch, other format errors, time-to-live exceeded, errors discovered in processing their IP options, etc."
    )
ipInAddrErrors = MibScalar((1, 3, 6, 1, 2, 1, 4, 5), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    ipInAddrErrors.setStatus("mandatory")
if mibBuilder.loadTexts:
    ipInAddrErrors.setDescription(
        "The number of input datagrams discarded because the IP address in their IP header's destination field was not a valid address to be received at this entity. This count includes invalid addresses (e.g., 0.0.0.0) and addresses of unsupported Classes (e.g., Class E). For entities which are not IP Gateways and therefore do not forward datagrams, this counter includes datagrams discarded because the destination address was not a local address."
    )
ipForwDatagrams = MibScalar((1, 3, 6, 1, 2, 1, 4, 6), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    ipForwDatagrams.setStatus("mandatory")
if mibBuilder.loadTexts:
    ipForwDatagrams.setDescription(
        "The number of input datagrams for which this entity was not their final IP destination, as a result of which an attempt was made to find a route to forward them to that final destination. In entities which do not act as IP Gateways, this counter will include only those packets which were Source-Routed via this entity, and the Source- Route option processing was successful."
    )
ipInUnknownProtos = MibScalar((1, 3, 6, 1, 2, 1, 4, 7), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    ipInUnknownProtos.setStatus("mandatory")
if mibBuilder.loadTexts:
    ipInUnknownProtos.setDescription(
        "The number of locally-addressed datagrams received successfully but discarded because of an unknown or unsupported protocol."
    )
ipInDiscards = MibScalar((1, 3, 6, 1, 2, 1, 4, 8), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    ipInDiscards.setStatus("mandatory")
if mibBuilder.loadTexts:
    ipInDiscards.setDescription(
        "The number of input IP datagrams for which no problems were encountered to prevent their continued processing, but which were discarded (e.g., for lack of buffer space). Note that this counter does not include any datagrams discarded while awaiting re-assembly."
    )
ipInDelivers = MibScalar((1, 3, 6, 1, 2, 1, 4, 9), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    ipInDelivers.setStatus("mandatory")
if mibBuilder.loadTexts:
    ipInDelivers.setDescription(
        "The total number of input datagrams successfully delivered to IP user-protocols (including ICMP)."
    )
ipOutRequests = MibScalar((1, 3, 6, 1, 2, 1, 4, 10), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    ipOutRequests.setStatus("mandatory")
if mibBuilder.loadTexts:
    ipOutRequests.setDescription(
        "The total number of IP datagrams which local IP user-protocols (including ICMP) supplied to IP in requests for transmission. Note that this counter does not include any datagrams counted in ipForwDatagrams."
    )
ipOutDiscards = MibScalar((1, 3, 6, 1, 2, 1, 4, 11), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    ipOutDiscards.setStatus("mandatory")
if mibBuilder.loadTexts:
    ipOutDiscards.setDescription(
        "The number of output IP datagrams for which no problem was encountered to prevent their transmission to their destination, but which were discarded (e.g., for lack of buffer space). Note that this counter would include datagrams counted in ipForwDatagrams if any such packets met this (discretionary) discard criterion."
    )
ipOutNoRoutes = MibScalar((1, 3, 6, 1, 2, 1, 4, 12), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    ipOutNoRoutes.setStatus("mandatory")
if mibBuilder.loadTexts:
    ipOutNoRoutes.setDescription(
        "The number of IP datagrams discarded because no route could be found to transmit them to their destination. Note that this counter includes any packets counted in ipForwDatagrams which meet this `no-route' criterion. Note that this includes any datagarms which a host cannot route because all of its default gateways are down."
    )
ipReasmTimeout = MibScalar((1, 3, 6, 1, 2, 1, 4, 13), Integer32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    ipReasmTimeout.setStatus("mandatory")
if mibBuilder.loadTexts:
    ipReasmTimeout.setDescription(
        "The maximum number of seconds which received fragments are held while they are awaiting reassembly at this entity."
    )
ipReasmReqds = MibScalar((1, 3, 6, 1, 2, 1, 4, 14), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    ipReasmReqds.setStatus("mandatory")
if mibBuilder.loadTexts:
    ipReasmReqds.setDescription(
        "The number of IP fragments received which needed to be reassembled at this entity."
    )
ipReasmOKs = MibScalar((1, 3, 6, 1, 2, 1, 4, 15), Counter32()).setMaxAccess("read-only")
if mibBuilder.loadTexts:
    ipReasmOKs.setStatus("mandatory")
if mibBuilder.loadTexts:
    ipReasmOKs.setDescription("The number of IP datagrams successfully re- assembled.")
ipReasmFails = MibScalar((1, 3, 6, 1, 2, 1, 4, 16), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    ipReasmFails.setStatus("mandatory")
if mibBuilder.loadTexts:
    ipReasmFails.setDescription(
        "The number of failures detected by the IP re- assembly algorithm (for whatever reason: timed out, errors, etc). Note that this is not necessarily a count of discarded IP fragments since some algorithms (notably the algorithm in RFC 815) can lose track of the number of fragments by combining them as they are received."
    )
ipFragOKs = MibScalar((1, 3, 6, 1, 2, 1, 4, 17), Counter32()).setMaxAccess("read-only")
if mibBuilder.loadTexts:
    ipFragOKs.setStatus("mandatory")
if mibBuilder.loadTexts:
    ipFragOKs.setDescription(
        "The number of IP datagrams that have been successfully fragmented at this entity."
    )
ipFragFails = MibScalar((1, 3, 6, 1, 2, 1, 4, 18), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    ipFragFails.setStatus("mandatory")
if mibBuilder.loadTexts:
    ipFragFails.setDescription(
        "The number of IP datagrams that have been discarded because they needed to be fragmented at this entity but could not be, e.g., because their Don't Fragment flag was set."
    )
ipFragCreates = MibScalar((1, 3, 6, 1, 2, 1, 4, 19), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    ipFragCreates.setStatus("mandatory")
if mibBuilder.loadTexts:
    ipFragCreates.setDescription(
        "The number of IP datagram fragments that have been generated as a result of fragmentation at this entity."
    )
ipAddrTable = MibTable(
    (1, 3, 6, 1, 2, 1, 4, 20),
)
if mibBuilder.loadTexts:
    ipAddrTable.setStatus("mandatory")
if mibBuilder.loadTexts:
    ipAddrTable.setDescription(
        "The table of addressing information relevant to this entity's IP addresses."
    )
ipAddrEntry = MibTableRow(
    (1, 3, 6, 1, 2, 1, 4, 20, 1),
).setIndexNames((0, "RFC1213-MIB", "ipAdEntAddr"))
if mibBuilder.loadTexts:
    ipAddrEntry.setStatus("mandatory")
if mibBuilder.loadTexts:
    ipAddrEntry.setDescription(
        "The addressing information for one of this entity's IP addresses."
    )
ipAdEntAddr = MibTableColumn((1, 3, 6, 1, 2, 1, 4, 20, 1, 1), IpAddress()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    ipAdEntAddr.setStatus("mandatory")
if mibBuilder.loadTexts:
    ipAdEntAddr.setDescription(
        "The IP address to which this entry's addressing information pertains."
    )
ipAdEntIfIndex = MibTableColumn(
    (1, 3, 6, 1, 2, 1, 4, 20, 1, 2), Integer32()
).setMaxAccess("read-only")
if mibBuilder.loadTexts:
    ipAdEntIfIndex.setStatus("mandatory")
if mibBuilder.loadTexts:
    ipAdEntIfIndex.setDescription(
        "The index value which uniquely identifies the interface to which this entry is applicable. The interface identified by a particular value of this index is the same interface as identified by the same value of ifIndex."
    )
ipAdEntNetMask = MibTableColumn(
    (1, 3, 6, 1, 2, 1, 4, 20, 1, 3), IpAddress()
).setMaxAccess("read-only")
if mibBuilder.loadTexts:
    ipAdEntNetMask.setStatus("mandatory")
if mibBuilder.loadTexts:
    ipAdEntNetMask.setDescription(
        "The subnet mask associated with the IP address of this entry. The value of the mask is an IP address with all the network bits set to 1 and all the hosts bits set to 0."
    )
ipAdEntBcastAddr = MibTableColumn(
    (1, 3, 6, 1, 2, 1, 4, 20, 1, 4), Integer32()
).setMaxAccess("read-only")
if mibBuilder.loadTexts:
    ipAdEntBcastAddr.setStatus("mandatory")
if mibBuilder.loadTexts:
    ipAdEntBcastAddr.setDescription(
        "The value of the least-significant bit in the IP broadcast address used for sending datagrams on the (logical) interface associated with the IP address of this entry. For example, when the Internet standard all-ones broadcast address is used, the value will be 1. This value applies to both the subnet and network broadcasts addresses used by the entity on this (logical) interface."
    )
ipAdEntReasmMaxSize = MibTableColumn(
    (1, 3, 6, 1, 2, 1, 4, 20, 1, 5),
    Integer32().subtype(subtypeSpec=ValueRangeConstraint(0, 65535)),
).setMaxAccess("read-only")
if mibBuilder.loadTexts:
    ipAdEntReasmMaxSize.setStatus("mandatory")
if mibBuilder.loadTexts:
    ipAdEntReasmMaxSize.setDescription(
        "The size of the largest IP datagram which this entity can re-assemble from incoming IP fragmented datagrams received on this interface."
    )
ipRouteTable = MibTable(
    (1, 3, 6, 1, 2, 1, 4, 21),
)
if mibBuilder.loadTexts:
    ipRouteTable.setStatus("mandatory")
if mibBuilder.loadTexts:
    ipRouteTable.setDescription("This entity's IP Routing table.")
ipRouteEntry = MibTableRow(
    (1, 3, 6, 1, 2, 1, 4, 21, 1),
).setIndexNames((0, "RFC1213-MIB", "ipRouteDest"))
if mibBuilder.loadTexts:
    ipRouteEntry.setStatus("mandatory")
if mibBuilder.loadTexts:
    ipRouteEntry.setDescription("A route to a particular destination.")
ipRouteDest = MibTableColumn((1, 3, 6, 1, 2, 1, 4, 21, 1, 1), IpAddress()).setMaxAccess(
    "read-write"
)
if mibBuilder.loadTexts:
    ipRouteDest.setStatus("mandatory")
if mibBuilder.loadTexts:
    ipRouteDest.setDescription(
        "The destination IP address of this route. An entry with a value of 0.0.0.0 is considered a default route. Multiple routes to a single destination can appear in the table, but access to such multiple entries is dependent on the table- access mechanisms defined by the network management protocol in use."
    )
ipRouteIfIndex = MibTableColumn(
    (1, 3, 6, 1, 2, 1, 4, 21, 1, 2), Integer32()
).setMaxAccess("read-write")
if mibBuilder.loadTexts:
    ipRouteIfIndex.setStatus("mandatory")
if mibBuilder.loadTexts:
    ipRouteIfIndex.setDescription(
        "The index value which uniquely identifies the local interface through which the next hop of this route should be reached. The interface identified by a particular value of this index is the same interface as identified by the same value of ifIndex."
    )
ipRouteMetric1 = MibTableColumn(
    (1, 3, 6, 1, 2, 1, 4, 21, 1, 3), Integer32()
).setMaxAccess("read-write")
if mibBuilder.loadTexts:
    ipRouteMetric1.setStatus("mandatory")
if mibBuilder.loadTexts:
    ipRouteMetric1.setDescription(
        "The primary routing metric for this route. The semantics of this metric are determined by the routing-protocol specified in the route's ipRouteProto value. If this metric is not used, its value should be set to -1."
    )
ipRouteMetric2 = MibTableColumn(
    (1, 3, 6, 1, 2, 1, 4, 21, 1, 4), Integer32()
).setMaxAccess("read-write")
if mibBuilder.loadTexts:
    ipRouteMetric2.setStatus("mandatory")
if mibBuilder.loadTexts:
    ipRouteMetric2.setDescription(
        "An alternate routing metric for this route. The semantics of this metric are determined by the routing-protocol specified in the route's ipRouteProto value. If this metric is not used, its value should be set to -1."
    )
ipRouteMetric3 = MibTableColumn(
    (1, 3, 6, 1, 2, 1, 4, 21, 1, 5), Integer32()
).setMaxAccess("read-write")
if mibBuilder.loadTexts:
    ipRouteMetric3.setStatus("mandatory")
if mibBuilder.loadTexts:
    ipRouteMetric3.setDescription(
        "An alternate routing metric for this route. The semantics of this metric are determined by the routing-protocol specified in the route's ipRouteProto value. If this metric is not used, its value should be set to -1."
    )
ipRouteMetric4 = MibTableColumn(
    (1, 3, 6, 1, 2, 1, 4, 21, 1, 6), Integer32()
).setMaxAccess("read-write")
if mibBuilder.loadTexts:
    ipRouteMetric4.setStatus("mandatory")
if mibBuilder.loadTexts:
    ipRouteMetric4.setDescription(
        "An alternate routing metric for this route. The semantics of this metric are determined by the routing-protocol specified in the route's ipRouteProto value. If this metric is not used, its value should be set to -1."
    )
ipRouteNextHop = MibTableColumn(
    (1, 3, 6, 1, 2, 1, 4, 21, 1, 7), IpAddress()
).setMaxAccess("read-write")
if mibBuilder.loadTexts:
    ipRouteNextHop.setStatus("mandatory")
if mibBuilder.loadTexts:
    ipRouteNextHop.setDescription(
        "The IP address of the next hop of this route. (In the case of a route bound to an interface which is realized via a broadcast media, the value of this field is the agent's IP address on that interface.)"
    )
ipRouteType = MibTableColumn(
    (1, 3, 6, 1, 2, 1, 4, 21, 1, 8),
    Integer32()
    .subtype(subtypeSpec=ConstraintsUnion(SingleValueConstraint(1, 2, 3, 4)))
    .clone(
        namedValues=NamedValues(
            ("other", 1), ("invalid", 2), ("direct", 3), ("indirect", 4)
        )
    ),
).setMaxAccess("read-write")
if mibBuilder.loadTexts:
    ipRouteType.setStatus("mandatory")
if mibBuilder.loadTexts:
    ipRouteType.setDescription(
        "The type of route. Note that the values direct(3) and indirect(4) refer to the notion of direct and indirect routing in the IP architecture. Setting this object to the value invalid(2) has the effect of invalidating the corresponding entry in the ipRouteTable object. That is, it effectively dissasociates the destination identified with said entry from the route identified with said entry. It is an implementation-specific matter as to whether the agent removes an invalidated entry from the table. Accordingly, management stations must be prepared to receive tabular information from agents that corresponds to entries not currently in use. Proper interpretation of such entries requires examination of the relevant ipRouteType object."
    )
ipRouteProto = MibTableColumn(
    (1, 3, 6, 1, 2, 1, 4, 21, 1, 9),
    Integer32()
    .subtype(
        subtypeSpec=ConstraintsUnion(
            SingleValueConstraint(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14)
        )
    )
    .clone(
        namedValues=NamedValues(
            ("other", 1),
            ("local", 2),
            ("netmgmt", 3),
            ("icmp", 4),
            ("egp", 5),
            ("ggp", 6),
            ("hello", 7),
            ("rip", 8),
            ("is-is", 9),
            ("es-is", 10),
            ("ciscoIgrp", 11),
            ("bbnSpfIgp", 12),
            ("ospf", 13),
            ("bgp", 14),
        )
    ),
).setMaxAccess("read-only")
if mibBuilder.loadTexts:
    ipRouteProto.setStatus("mandatory")
if mibBuilder.loadTexts:
    ipRouteProto.setDescription(
        "The routing mechanism via which this route was learned. Inclusion of values for gateway routing protocols is not intended to imply that hosts should support those protocols."
    )
ipRouteAge = MibTableColumn((1, 3, 6, 1, 2, 1, 4, 21, 1, 10), Integer32()).setMaxAccess(
    "read-write"
)
if mibBuilder.loadTexts:
    ipRouteAge.setStatus("mandatory")
if mibBuilder.loadTexts:
    ipRouteAge.setDescription(
        "The number of seconds since this route was last updated or otherwise determined to be correct. Note that no semantics of `too old' can be implied except through knowledge of the routing protocol by which the route was learned."
    )
ipRouteMask = MibTableColumn(
    (1, 3, 6, 1, 2, 1, 4, 21, 1, 11), IpAddress()
).setMaxAccess("read-write")
if mibBuilder.loadTexts:
    ipRouteMask.setStatus("mandatory")
if mibBuilder.loadTexts:
    ipRouteMask.setDescription(
        "Indicate the mask to be logical-ANDed with the destination address before being compared to the value in the ipRouteDest field. For those systems that do not support arbitrary subnet masks, an agent constructs the value of the ipRouteMask by determining whether the value of the correspondent ipRouteDest field belong to a class-A, B, or C network, and then using one of: mask network 255.0.0.0 class-A 255.255.0.0 class-B 255.255.255.0 class-C If the value of the ipRouteDest is 0.0.0.0 (a default route), then the mask value is also 0.0.0.0. It should be noted that all IP routing subsystems implicitly use this mechanism."
    )
ipRouteMetric5 = MibTableColumn(
    (1, 3, 6, 1, 2, 1, 4, 21, 1, 12), Integer32()
).setMaxAccess("read-write")
if mibBuilder.loadTexts:
    ipRouteMetric5.setStatus("mandatory")
if mibBuilder.loadTexts:
    ipRouteMetric5.setDescription(
        "An alternate routing metric for this route. The semantics of this metric are determined by the routing-protocol specified in the route's ipRouteProto value. If this metric is not used, its value should be set to -1."
    )
ipRouteInfo = MibTableColumn(
    (1, 3, 6, 1, 2, 1, 4, 21, 1, 13), ObjectIdentifier()
).setMaxAccess("read-only")
if mibBuilder.loadTexts:
    ipRouteInfo.setStatus("mandatory")
if mibBuilder.loadTexts:
    ipRouteInfo.setDescription(
        "A reference to MIB definitions specific to the particular routing protocol which is responsible for this route, as determined by the value specified in the route's ipRouteProto value. If this information is not present, its value should be set to the OBJECT IDENTIFIER { 0 0 }, which is a syntatically valid object identifier, and any conformant implementation of ASN.1 and BER must be able to generate and recognize this value."
    )
ipNetToMediaTable = MibTable(
    (1, 3, 6, 1, 2, 1, 4, 22),
)
if mibBuilder.loadTexts:
    ipNetToMediaTable.setStatus("mandatory")
if mibBuilder.loadTexts:
    ipNetToMediaTable.setDescription(
        "The IP Address Translation table used for mapping from IP addresses to physical addresses."
    )
ipNetToMediaEntry = MibTableRow(
    (1, 3, 6, 1, 2, 1, 4, 22, 1),
).setIndexNames(
    (0, "RFC1213-MIB", "ipNetToMediaIfIndex"),
    (0, "RFC1213-MIB", "ipNetToMediaNetAddress"),
)
if mibBuilder.loadTexts:
    ipNetToMediaEntry.setStatus("mandatory")
if mibBuilder.loadTexts:
    ipNetToMediaEntry.setDescription(
        "Each entry contains one IpAddress to `physical' address equivalence."
    )
ipNetToMediaIfIndex = MibTableColumn(
    (1, 3, 6, 1, 2, 1, 4, 22, 1, 1), Integer32()
).setMaxAccess("read-write")
if mibBuilder.loadTexts:
    ipNetToMediaIfIndex.setStatus("mandatory")
if mibBuilder.loadTexts:
    ipNetToMediaIfIndex.setDescription(
        "The interface on which this entry's equivalence is effective. The interface identified by a particular value of this index is the same interface as identified by the same value of ifIndex."
    )
ipNetToMediaPhysAddress = MibTableColumn(
    (1, 3, 6, 1, 2, 1, 4, 22, 1, 2), PhysAddress()
).setMaxAccess("read-write")
if mibBuilder.loadTexts:
    ipNetToMediaPhysAddress.setStatus("mandatory")
if mibBuilder.loadTexts:
    ipNetToMediaPhysAddress.setDescription("The media-dependent `physical' address.")
ipNetToMediaNetAddress = MibTableColumn(
    (1, 3, 6, 1, 2, 1, 4, 22, 1, 3), IpAddress()
).setMaxAccess("read-write")
if mibBuilder.loadTexts:
    ipNetToMediaNetAddress.setStatus("mandatory")
if mibBuilder.loadTexts:
    ipNetToMediaNetAddress.setDescription(
        "The IpAddress corresponding to the media- dependent `physical' address."
    )
ipNetToMediaType = MibTableColumn(
    (1, 3, 6, 1, 2, 1, 4, 22, 1, 4),
    Integer32()
    .subtype(subtypeSpec=ConstraintsUnion(SingleValueConstraint(1, 2, 3, 4)))
    .clone(
        namedValues=NamedValues(
            ("other", 1), ("invalid", 2), ("dynamic", 3), ("static", 4)
        )
    ),
).setMaxAccess("read-write")
if mibBuilder.loadTexts:
    ipNetToMediaType.setStatus("mandatory")
if mibBuilder.loadTexts:
    ipNetToMediaType.setDescription(
        "The type of mapping. Setting this object to the value invalid(2) has the effect of invalidating the corresponding entry in the ipNetToMediaTable. That is, it effectively dissasociates the interface identified with said entry from the mapping identified with said entry. It is an implementation-specific matter as to whether the agent removes an invalidated entry from the table. Accordingly, management stations must be prepared to receive tabular information from agents that corresponds to entries not currently in use. Proper interpretation of such entries requires examination of the relevant ipNetToMediaType object."
    )
ipRoutingDiscards = MibScalar((1, 3, 6, 1, 2, 1, 4, 23), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    ipRoutingDiscards.setStatus("mandatory")
if mibBuilder.loadTexts:
    ipRoutingDiscards.setDescription(
        "The number of routing entries which were chosen to be discarded even though they are valid. One possible reason for discarding such an entry could be to free-up buffer space for other routing entries."
    )
icmpInMsgs = MibScalar((1, 3, 6, 1, 2, 1, 5, 1), Counter32()).setMaxAccess("read-only")
if mibBuilder.loadTexts:
    icmpInMsgs.setStatus("mandatory")
if mibBuilder.loadTexts:
    icmpInMsgs.setDescription(
        "The total number of ICMP messages which the entity received. Note that this counter includes all those counted by icmpInErrors."
    )
icmpInErrors = MibScalar((1, 3, 6, 1, 2, 1, 5, 2), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    icmpInErrors.setStatus("mandatory")
if mibBuilder.loadTexts:
    icmpInErrors.setDescription(
        "The number of ICMP messages which the entity received but determined as having ICMP-specific errors (bad ICMP checksums, bad length, etc.)."
    )
icmpInDestUnreachs = MibScalar((1, 3, 6, 1, 2, 1, 5, 3), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    icmpInDestUnreachs.setStatus("mandatory")
if mibBuilder.loadTexts:
    icmpInDestUnreachs.setDescription(
        "The number of ICMP Destination Unreachable messages received."
    )
icmpInTimeExcds = MibScalar((1, 3, 6, 1, 2, 1, 5, 4), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    icmpInTimeExcds.setStatus("mandatory")
if mibBuilder.loadTexts:
    icmpInTimeExcds.setDescription(
        "The number of ICMP Time Exceeded messages received."
    )
icmpInParmProbs = MibScalar((1, 3, 6, 1, 2, 1, 5, 5), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    icmpInParmProbs.setStatus("mandatory")
if mibBuilder.loadTexts:
    icmpInParmProbs.setDescription(
        "The number of ICMP Parameter Problem messages received."
    )
icmpInSrcQuenchs = MibScalar((1, 3, 6, 1, 2, 1, 5, 6), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    icmpInSrcQuenchs.setStatus("mandatory")
if mibBuilder.loadTexts:
    icmpInSrcQuenchs.setDescription(
        "The number of ICMP Source Quench messages received."
    )
icmpInRedirects = MibScalar((1, 3, 6, 1, 2, 1, 5, 7), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    icmpInRedirects.setStatus("mandatory")
if mibBuilder.loadTexts:
    icmpInRedirects.setDescription("The number of ICMP Redirect messages received.")
icmpInEchos = MibScalar((1, 3, 6, 1, 2, 1, 5, 8), Counter32()).setMaxAccess("read-only")
if mibBuilder.loadTexts:
    icmpInEchos.setStatus("mandatory")
if mibBuilder.loadTexts:
    icmpInEchos.setDescription("The number of ICMP Echo (request) messages received.")
icmpInEchoReps = MibScalar((1, 3, 6, 1, 2, 1, 5, 9), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    icmpInEchoReps.setStatus("mandatory")
if mibBuilder.loadTexts:
    icmpInEchoReps.setDescription("The number of ICMP Echo Reply messages received.")
icmpInTimestamps = MibScalar((1, 3, 6, 1, 2, 1, 5, 10), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    icmpInTimestamps.setStatus("mandatory")
if mibBuilder.loadTexts:
    icmpInTimestamps.setDescription(
        "The number of ICMP Timestamp (request) messages received."
    )
icmpInTimestampReps = MibScalar((1, 3, 6, 1, 2, 1, 5, 11), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    icmpInTimestampReps.setStatus("mandatory")
if mibBuilder.loadTexts:
    icmpInTimestampReps.setDescription(
        "The number of ICMP Timestamp Reply messages received."
    )
icmpInAddrMasks = MibScalar((1, 3, 6, 1, 2, 1, 5, 12), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    icmpInAddrMasks.setStatus("mandatory")
if mibBuilder.loadTexts:
    icmpInAddrMasks.setDescription(
        "The number of ICMP Address Mask Request messages received."
    )
icmpInAddrMaskReps = MibScalar((1, 3, 6, 1, 2, 1, 5, 13), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    icmpInAddrMaskReps.setStatus("mandatory")
if mibBuilder.loadTexts:
    icmpInAddrMaskReps.setDescription(
        "The number of ICMP Address Mask Reply messages received."
    )
icmpOutMsgs = MibScalar((1, 3, 6, 1, 2, 1, 5, 14), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    icmpOutMsgs.setStatus("mandatory")
if mibBuilder.loadTexts:
    icmpOutMsgs.setDescription(
        "The total number of ICMP messages which this entity attempted to send. Note that this counter includes all those counted by icmpOutErrors."
    )
icmpOutErrors = MibScalar((1, 3, 6, 1, 2, 1, 5, 15), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    icmpOutErrors.setStatus("mandatory")
if mibBuilder.loadTexts:
    icmpOutErrors.setDescription(
        "The number of ICMP messages which this entity did not send due to problems discovered within ICMP such as a lack of buffers. This value should not include errors discovered outside the ICMP layer such as the inability of IP to route the resultant datagram. In some implementations there may be no types of error which contribute to this counter's value."
    )
icmpOutDestUnreachs = MibScalar((1, 3, 6, 1, 2, 1, 5, 16), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    icmpOutDestUnreachs.setStatus("mandatory")
if mibBuilder.loadTexts:
    icmpOutDestUnreachs.setDescription(
        "The number of ICMP Destination Unreachable messages sent."
    )
icmpOutTimeExcds = MibScalar((1, 3, 6, 1, 2, 1, 5, 17), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    icmpOutTimeExcds.setStatus("mandatory")
if mibBuilder.loadTexts:
    icmpOutTimeExcds.setDescription("The number of ICMP Time Exceeded messages sent.")
icmpOutParmProbs = MibScalar((1, 3, 6, 1, 2, 1, 5, 18), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    icmpOutParmProbs.setStatus("mandatory")
if mibBuilder.loadTexts:
    icmpOutParmProbs.setDescription(
        "The number of ICMP Parameter Problem messages sent."
    )
icmpOutSrcQuenchs = MibScalar((1, 3, 6, 1, 2, 1, 5, 19), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    icmpOutSrcQuenchs.setStatus("mandatory")
if mibBuilder.loadTexts:
    icmpOutSrcQuenchs.setDescription("The number of ICMP Source Quench messages sent.")
icmpOutRedirects = MibScalar((1, 3, 6, 1, 2, 1, 5, 20), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    icmpOutRedirects.setStatus("mandatory")
if mibBuilder.loadTexts:
    icmpOutRedirects.setDescription(
        "The number of ICMP Redirect messages sent. For a host, this object will always be zero, since hosts do not send redirects."
    )
icmpOutEchos = MibScalar((1, 3, 6, 1, 2, 1, 5, 21), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    icmpOutEchos.setStatus("mandatory")
if mibBuilder.loadTexts:
    icmpOutEchos.setDescription("The number of ICMP Echo (request) messages sent.")
icmpOutEchoReps = MibScalar((1, 3, 6, 1, 2, 1, 5, 22), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    icmpOutEchoReps.setStatus("mandatory")
if mibBuilder.loadTexts:
    icmpOutEchoReps.setDescription("The number of ICMP Echo Reply messages sent.")
icmpOutTimestamps = MibScalar((1, 3, 6, 1, 2, 1, 5, 23), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    icmpOutTimestamps.setStatus("mandatory")
if mibBuilder.loadTexts:
    icmpOutTimestamps.setDescription(
        "The number of ICMP Timestamp (request) messages sent."
    )
icmpOutTimestampReps = MibScalar((1, 3, 6, 1, 2, 1, 5, 24), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    icmpOutTimestampReps.setStatus("mandatory")
if mibBuilder.loadTexts:
    icmpOutTimestampReps.setDescription(
        "The number of ICMP Timestamp Reply messages sent."
    )
icmpOutAddrMasks = MibScalar((1, 3, 6, 1, 2, 1, 5, 25), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    icmpOutAddrMasks.setStatus("mandatory")
if mibBuilder.loadTexts:
    icmpOutAddrMasks.setDescription(
        "The number of ICMP Address Mask Request messages sent."
    )
icmpOutAddrMaskReps = MibScalar((1, 3, 6, 1, 2, 1, 5, 26), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    icmpOutAddrMaskReps.setStatus("mandatory")
if mibBuilder.loadTexts:
    icmpOutAddrMaskReps.setDescription(
        "The number of ICMP Address Mask Reply messages sent."
    )
tcpRtoAlgorithm = MibScalar(
    (1, 3, 6, 1, 2, 1, 6, 1),
    Integer32()
    .subtype(subtypeSpec=ConstraintsUnion(SingleValueConstraint(1, 2, 3, 4)))
    .clone(
        namedValues=NamedValues(("other", 1), ("constant", 2), ("rsre", 3), ("vanj", 4))
    ),
).setMaxAccess("read-only")
if mibBuilder.loadTexts:
    tcpRtoAlgorithm.setStatus("mandatory")
if mibBuilder.loadTexts:
    tcpRtoAlgorithm.setDescription(
        "The algorithm used to determine the timeout value used for retransmitting unacknowledged octets."
    )
tcpRtoMin = MibScalar((1, 3, 6, 1, 2, 1, 6, 2), Integer32()).setMaxAccess("read-only")
if mibBuilder.loadTexts:
    tcpRtoMin.setStatus("mandatory")
if mibBuilder.loadTexts:
    tcpRtoMin.setDescription(
        "The minimum value permitted by a TCP implementation for the retransmission timeout, measured in milliseconds. More refined semantics for objects of this type depend upon the algorithm used to determine the retransmission timeout. In particular, when the timeout algorithm is rsre(3), an object of this type has the semantics of the LBOUND quantity described in RFC 793."
    )
tcpRtoMax = MibScalar((1, 3, 6, 1, 2, 1, 6, 3), Integer32()).setMaxAccess("read-only")
if mibBuilder.loadTexts:
    tcpRtoMax.setStatus("mandatory")
if mibBuilder.loadTexts:
    tcpRtoMax.setDescription(
        "The maximum value permitted by a TCP implementation for the retransmission timeout, measured in milliseconds. More refined semantics for objects of this type depend upon the algorithm used to determine the retransmission timeout. In particular, when the timeout algorithm is rsre(3), an object of this type has the semantics of the UBOUND quantity described in RFC 793."
    )
tcpMaxConn = MibScalar((1, 3, 6, 1, 2, 1, 6, 4), Integer32()).setMaxAccess("read-only")
if mibBuilder.loadTexts:
    tcpMaxConn.setStatus("mandatory")
if mibBuilder.loadTexts:
    tcpMaxConn.setDescription(
        "The limit on the total number of TCP connections the entity can support. In entities where the maximum number of connections is dynamic, this object should contain the value -1."
    )
tcpActiveOpens = MibScalar((1, 3, 6, 1, 2, 1, 6, 5), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    tcpActiveOpens.setStatus("mandatory")
if mibBuilder.loadTexts:
    tcpActiveOpens.setDescription(
        "The number of times TCP connections have made a direct transition to the SYN-SENT state from the CLOSED state."
    )
tcpPassiveOpens = MibScalar((1, 3, 6, 1, 2, 1, 6, 6), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    tcpPassiveOpens.setStatus("mandatory")
if mibBuilder.loadTexts:
    tcpPassiveOpens.setDescription(
        "The number of times TCP connections have made a direct transition to the SYN-RCVD state from the LISTEN state."
    )
tcpAttemptFails = MibScalar((1, 3, 6, 1, 2, 1, 6, 7), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    tcpAttemptFails.setStatus("mandatory")
if mibBuilder.loadTexts:
    tcpAttemptFails.setDescription(
        "The number of times TCP connections have made a direct transition to the CLOSED state from either the SYN-SENT state or the SYN-RCVD state, plus the number of times TCP connections have made a direct transition to the LISTEN state from the SYN-RCVD state."
    )
tcpEstabResets = MibScalar((1, 3, 6, 1, 2, 1, 6, 8), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    tcpEstabResets.setStatus("mandatory")
if mibBuilder.loadTexts:
    tcpEstabResets.setDescription(
        "The number of times TCP connections have made a direct transition to the CLOSED state from either the ESTABLISHED state or the CLOSE-WAIT state."
    )
tcpCurrEstab = MibScalar((1, 3, 6, 1, 2, 1, 6, 9), Gauge32()).setMaxAccess("read-only")
if mibBuilder.loadTexts:
    tcpCurrEstab.setStatus("mandatory")
if mibBuilder.loadTexts:
    tcpCurrEstab.setDescription(
        "The number of TCP connections for which the current state is either ESTABLISHED or CLOSE- WAIT."
    )
tcpInSegs = MibScalar((1, 3, 6, 1, 2, 1, 6, 10), Counter32()).setMaxAccess("read-only")
if mibBuilder.loadTexts:
    tcpInSegs.setStatus("mandatory")
if mibBuilder.loadTexts:
    tcpInSegs.setDescription(
        "The total number of segments received, including those received in error. This count includes segments received on currently established connections."
    )
tcpOutSegs = MibScalar((1, 3, 6, 1, 2, 1, 6, 11), Counter32()).setMaxAccess("read-only")
if mibBuilder.loadTexts:
    tcpOutSegs.setStatus("mandatory")
if mibBuilder.loadTexts:
    tcpOutSegs.setDescription(
        "The total number of segments sent, including those on current connections but excluding those containing only retransmitted octets."
    )
tcpRetransSegs = MibScalar((1, 3, 6, 1, 2, 1, 6, 12), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    tcpRetransSegs.setStatus("mandatory")
if mibBuilder.loadTexts:
    tcpRetransSegs.setDescription(
        "The total number of segments retransmitted - that is, the number of TCP segments transmitted containing one or more previously transmitted octets."
    )
tcpConnTable = MibTable(
    (1, 3, 6, 1, 2, 1, 6, 13),
)
if mibBuilder.loadTexts:
    tcpConnTable.setStatus("mandatory")
if mibBuilder.loadTexts:
    tcpConnTable.setDescription(
        "A table containing TCP connection-specific information."
    )
tcpConnEntry = MibTableRow(
    (1, 3, 6, 1, 2, 1, 6, 13, 1),
).setIndexNames(
    (0, "RFC1213-MIB", "tcpConnLocalAddress"),
    (0, "RFC1213-MIB", "tcpConnLocalPort"),
    (0, "RFC1213-MIB", "tcpConnRemAddress"),
    (0, "RFC1213-MIB", "tcpConnRemPort"),
)
if mibBuilder.loadTexts:
    tcpConnEntry.setStatus("mandatory")
if mibBuilder.loadTexts:
    tcpConnEntry.setDescription(
        "Information about a particular current TCP connection. An object of this type is transient, in that it ceases to exist when (or soon after) the connection makes the transition to the CLOSED state."
    )
tcpConnState = MibTableColumn(
    (1, 3, 6, 1, 2, 1, 6, 13, 1, 1),
    Integer32()
    .subtype(
        subtypeSpec=ConstraintsUnion(
            SingleValueConstraint(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)
        )
    )
    .clone(
        namedValues=NamedValues(
            ("closed", 1),
            ("listen", 2),
            ("synSent", 3),
            ("synReceived", 4),
            ("established", 5),
            ("finWait1", 6),
            ("finWait2", 7),
            ("closeWait", 8),
            ("lastAck", 9),
            ("closing", 10),
            ("timeWait", 11),
            ("deleteTCB", 12),
        )
    ),
).setMaxAccess("read-write")
if mibBuilder.loadTexts:
    tcpConnState.setStatus("mandatory")
if mibBuilder.loadTexts:
    tcpConnState.setDescription(
        "The state of this TCP connection. The only value which may be set by a management station is deleteTCB(12). Accordingly, it is appropriate for an agent to return a `badValue' response if a management station attempts to set this object to any other value. If a management station sets this object to the value deleteTCB(12), then this has the effect of deleting the TCB (as defined in RFC 793) of the corresponding connection on the managed node, resulting in immediate termination of the connection. As an implementation-specific option, a RST segment may be sent from the managed node to the other TCP endpoint (note however that RST segments are not sent reliably)."
    )
tcpConnLocalAddress = MibTableColumn(
    (1, 3, 6, 1, 2, 1, 6, 13, 1, 2), IpAddress()
).setMaxAccess("read-only")
if mibBuilder.loadTexts:
    tcpConnLocalAddress.setStatus("mandatory")
if mibBuilder.loadTexts:
    tcpConnLocalAddress.setDescription(
        "The local IP address for this TCP connection. In the case of a connection in the listen state which is willing to accept connections for any IP interface associated with the node, the value 0.0.0.0 is used."
    )
tcpConnLocalPort = MibTableColumn(
    (1, 3, 6, 1, 2, 1, 6, 13, 1, 3),
    Integer32().subtype(subtypeSpec=ValueRangeConstraint(0, 65535)),
).setMaxAccess("read-only")
if mibBuilder.loadTexts:
    tcpConnLocalPort.setStatus("mandatory")
if mibBuilder.loadTexts:
    tcpConnLocalPort.setDescription("The local port number for this TCP connection.")
tcpConnRemAddress = MibTableColumn(
    (1, 3, 6, 1, 2, 1, 6, 13, 1, 4), IpAddress()
).setMaxAccess("read-only")
if mibBuilder.loadTexts:
    tcpConnRemAddress.setStatus("mandatory")
if mibBuilder.loadTexts:
    tcpConnRemAddress.setDescription("The remote IP address for this TCP connection.")
tcpConnRemPort = MibTableColumn(
    (1, 3, 6, 1, 2, 1, 6, 13, 1, 5),
    Integer32().subtype(subtypeSpec=ValueRangeConstraint(0, 65535)),
).setMaxAccess("read-only")
if mibBuilder.loadTexts:
    tcpConnRemPort.setStatus("mandatory")
if mibBuilder.loadTexts:
    tcpConnRemPort.setDescription("The remote port number for this TCP connection.")
tcpInErrs = MibScalar((1, 3, 6, 1, 2, 1, 6, 14), Counter32()).setMaxAccess("read-only")
if mibBuilder.loadTexts:
    tcpInErrs.setStatus("mandatory")
if mibBuilder.loadTexts:
    tcpInErrs.setDescription(
        "The total number of segments received in error (e.g., bad TCP checksums)."
    )
tcpOutRsts = MibScalar((1, 3, 6, 1, 2, 1, 6, 15), Counter32()).setMaxAccess("read-only")
if mibBuilder.loadTexts:
    tcpOutRsts.setStatus("mandatory")
if mibBuilder.loadTexts:
    tcpOutRsts.setDescription(
        "The number of TCP segments sent containing the RST flag."
    )
udpInDatagrams = MibScalar((1, 3, 6, 1, 2, 1, 7, 1), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    udpInDatagrams.setStatus("mandatory")
if mibBuilder.loadTexts:
    udpInDatagrams.setDescription(
        "The total number of UDP datagrams delivered to UDP users."
    )
udpNoPorts = MibScalar((1, 3, 6, 1, 2, 1, 7, 2), Counter32()).setMaxAccess("read-only")
if mibBuilder.loadTexts:
    udpNoPorts.setStatus("mandatory")
if mibBuilder.loadTexts:
    udpNoPorts.setDescription(
        "The total number of received UDP datagrams for which there was no application at the destination port."
    )
udpInErrors = MibScalar((1, 3, 6, 1, 2, 1, 7, 3), Counter32()).setMaxAccess("read-only")
if mibBuilder.loadTexts:
    udpInErrors.setStatus("mandatory")
if mibBuilder.loadTexts:
    udpInErrors.setDescription(
        "The number of received UDP datagrams that could not be delivered for reasons other than the lack of an application at the destination port."
    )
udpOutDatagrams = MibScalar((1, 3, 6, 1, 2, 1, 7, 4), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    udpOutDatagrams.setStatus("mandatory")
if mibBuilder.loadTexts:
    udpOutDatagrams.setDescription(
        "The total number of UDP datagrams sent from this entity."
    )
udpTable = MibTable(
    (1, 3, 6, 1, 2, 1, 7, 5),
)
if mibBuilder.loadTexts:
    udpTable.setStatus("mandatory")
if mibBuilder.loadTexts:
    udpTable.setDescription("A table containing UDP listener information.")
udpEntry = MibTableRow(
    (1, 3, 6, 1, 2, 1, 7, 5, 1),
).setIndexNames(
    (0, "RFC1213-MIB", "udpLocalAddress"), (0, "RFC1213-MIB", "udpLocalPort")
)
if mibBuilder.loadTexts:
    udpEntry.setStatus("mandatory")
if mibBuilder.loadTexts:
    udpEntry.setDescription("Information about a particular current UDP listener.")
udpLocalAddress = MibTableColumn(
    (1, 3, 6, 1, 2, 1, 7, 5, 1, 1), IpAddress()
).setMaxAccess("read-only")
if mibBuilder.loadTexts:
    udpLocalAddress.setStatus("mandatory")
if mibBuilder.loadTexts:
    udpLocalAddress.setDescription(
        "The local IP address for this UDP listener. In the case of a UDP listener which is willing to accept datagrams for any IP interface associated with the node, the value 0.0.0.0 is used."
    )
udpLocalPort = MibTableColumn(
    (1, 3, 6, 1, 2, 1, 7, 5, 1, 2),
    Integer32().subtype(subtypeSpec=ValueRangeConstraint(0, 65535)),
).setMaxAccess("read-only")
if mibBuilder.loadTexts:
    udpLocalPort.setStatus("mandatory")
if mibBuilder.loadTexts:
    udpLocalPort.setDescription("The local port number for this UDP listener.")
egpInMsgs = MibScalar((1, 3, 6, 1, 2, 1, 8, 1), Counter32()).setMaxAccess("read-only")
if mibBuilder.loadTexts:
    egpInMsgs.setStatus("mandatory")
if mibBuilder.loadTexts:
    egpInMsgs.setDescription("The number of EGP messages received without error.")
egpInErrors = MibScalar((1, 3, 6, 1, 2, 1, 8, 2), Counter32()).setMaxAccess("read-only")
if mibBuilder.loadTexts:
    egpInErrors.setStatus("mandatory")
if mibBuilder.loadTexts:
    egpInErrors.setDescription(
        "The number of EGP messages received that proved to be in error."
    )
egpOutMsgs = MibScalar((1, 3, 6, 1, 2, 1, 8, 3), Counter32()).setMaxAccess("read-only")
if mibBuilder.loadTexts:
    egpOutMsgs.setStatus("mandatory")
if mibBuilder.loadTexts:
    egpOutMsgs.setDescription("The total number of locally generated EGP messages.")
egpOutErrors = MibScalar((1, 3, 6, 1, 2, 1, 8, 4), Counter32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    egpOutErrors.setStatus("mandatory")
if mibBuilder.loadTexts:
    egpOutErrors.setDescription(
        "The number of locally generated EGP messages not sent due to resource limitations within an EGP entity."
    )
egpNeighTable = MibTable(
    (1, 3, 6, 1, 2, 1, 8, 5),
)
if mibBuilder.loadTexts:
    egpNeighTable.setStatus("mandatory")
if mibBuilder.loadTexts:
    egpNeighTable.setDescription("The EGP neighbor table.")
egpNeighEntry = MibTableRow(
    (1, 3, 6, 1, 2, 1, 8, 5, 1),
).setIndexNames((0, "RFC1213-MIB", "egpNeighAddr"))
if mibBuilder.loadTexts:
    egpNeighEntry.setStatus("mandatory")
if mibBuilder.loadTexts:
    egpNeighEntry.setDescription(
        "Information about this entity's relationship with a particular EGP neighbor."
    )
egpNeighState = MibTableColumn(
    (1, 3, 6, 1, 2, 1, 8, 5, 1, 1),
    Integer32()
    .subtype(subtypeSpec=ConstraintsUnion(SingleValueConstraint(1, 2, 3, 4, 5)))
    .clone(
        namedValues=NamedValues(
            ("idle", 1), ("acquisition", 2), ("down", 3), ("up", 4), ("cease", 5)
        )
    ),
).setMaxAccess("read-only")
if mibBuilder.loadTexts:
    egpNeighState.setStatus("mandatory")
if mibBuilder.loadTexts:
    egpNeighState.setDescription(
        "The EGP state of the local system with respect to this entry's EGP neighbor. Each EGP state is represented by a value that is one greater than the numerical value associated with said state in RFC 904."
    )
egpNeighAddr = MibTableColumn((1, 3, 6, 1, 2, 1, 8, 5, 1, 2), IpAddress()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    egpNeighAddr.setStatus("mandatory")
if mibBuilder.loadTexts:
    egpNeighAddr.setDescription("The IP address of this entry's EGP neighbor.")
egpNeighAs = MibTableColumn((1, 3, 6, 1, 2, 1, 8, 5, 1, 3), Integer32()).setMaxAccess(
    "read-only"
)
if mibBuilder.loadTexts:
    egpNeighAs.setStatus("mandatory")
if mibBuilder.loadTexts:
    egpNeighAs.setDescription(
        "The autonomous system of this EGP peer. Zero should be specified if the autonomous system number of the neighbor is not yet known."
    )
egpNeighInMsgs = MibTableColumn(
    (1, 3, 6, 1, 2, 1, 8, 5, 1, 4), Counter32()
).setMaxAccess("read-only")
if mibBuilder.loadTexts:
    egpNeighInMsgs.setStatus("mandatory")
if mibBuilder.loadTexts:
    egpNeighInMsgs.setDescription(
        "The number of EGP messages received without error from this EGP peer."
    )
egpNeighInErrs = MibTableColumn(
    (1, 3, 6, 1, 2, 1, 8, 5, 1, 5), Counter32()
).setMaxAccess("read-only")
if mibBuilder.loadTexts:
    egpNeighInErrs.setStatus("mandatory")
if mibBuilder.loadTexts:
    egpNeighInErrs.setDescription(
        "The number of EGP messages received from this EGP peer that proved to be in error (e.g., bad EGP checksum)."
    )
egpNeighOutMsgs = MibTableColumn(
    (1, 3, 6, 1, 2, 1, 8, 5, 1, 6), Counter32()
).setMaxAccess("read-only")
if mibBuilder.loadTexts:
    egpNeighOutMsgs.setStatus("mandatory")
if mibBuilder.loadTexts:
    egpNeighOutMsgs.setDescription(
        "The number of locally generated EGP messages to this EGP peer."
    )
egpNeighOutErrs = MibTableColumn(
    (1, 3, 6, 1, 2, 1, 8, 5, 1, 7), Counter32()
).setMaxAccess("read-only")
if mibBuilder.loadTexts:
    egpNeighOutErrs.setStatus("mandatory")
if mibBuilder.loadTexts:
    egpNeighOutErrs.setDescription(
        "The number of locally generated EGP messages not sent to this EGP peer due to resource limitations within an EGP entity."
    )
egpNeighInErrMsgs = MibTableColumn(
    (1, 3, 6, 1, 2, 1, 8, 5, 1, 8), Counter32()
).setMaxAccess("read-only")
if mibBuilder.loadTexts:
    egpNeighInErrMsgs.setStatus("mandatory")
if mibBuilder.loadTexts:
    egpNeighInErrMsgs.setDescription(
        "The number of EGP-defined error messages received from this EGP peer."
    )
egpNeighOutErrMsgs = MibTableColumn(
    (1, 3, 6, 1, 2, 1, 8, 5, 1, 9), Counter32()
).setMaxAccess("read-only")
if mibBuilder.loadTexts:
    egpNeighOutErrMsgs.setStatus("mandatory")
if mibBuilder.loadTexts:
    egpNeighOutErrMsgs.setDescription(
        "The number of EGP-defined error messages sent to this EGP peer."
    )
egpNeighStateUps = MibTableColumn(
    (1, 3, 6, 1, 2, 1, 8, 5, 1, 10), Counter32()
).setMaxAccess("read-only")
if mibBuilder.loadTexts:
    egpNeighStateUps.setStatus("mandatory")
if mibBuilder.loadTexts:
    egpNeighStateUps.setDescription(
        "The number of EGP state transitions to the UP state with this EGP peer."
    )
egpNeighStateDowns = MibTableColumn(
    (1, 3, 6, 1, 2, 1, 8, 5, 1, 11), Counter32()
).setMaxAccess("read-only")
if mibBuilder.loadTexts:
    egpNeighStateDowns.setStatus("mandatory")
if mibBuilder.loadTexts:
    egpNeighStateDowns.setDescription(
        "The number of EGP state transitions from the UP state to any other state with this EGP peer."
    )
egpNeighIntervalHello = MibTableColumn(
    (1, 3, 6, 1, 2, 1, 8, 5, 1, 12), Integer32()
).setMaxAccess("read-only")
if mibBuilder.loadTexts:
    egpNeighIntervalHello.setStatus("mandatory")
if mibBuilder.loadTexts:
    egpNeighIntervalHello.setDescription(
        "The interval between EGP Hello command retransmissions (in hundredths of a second). This represents the t1 timer as defined in RFC 904."
    )
egpNeighIntervalPoll = MibTableColumn(
    (1, 3, 6, 1, 2, 1, 8, 5, 1, 13), Integer32()
).setMaxAccess("read-only")
if mibBuilder.loadTexts:
    egpNeighIntervalPoll.setStatus("mandatory")
if mibBuilder.loadTexts:
    egpNeighIntervalPoll.setDescription(
        "The interval between EGP poll command retransmissions (in hundredths of a second). This represents the t3 timer as defined in RFC 904."
    )
egpNeighMode = MibTableColumn(
    (1, 3, 6, 1, 2, 1, 8, 5, 1, 14),
    Integer32()
    .subtype(subtypeSpec=ConstraintsUnion(SingleValueConstraint(1, 2)))
    .clone(namedValues=NamedValues(("active", 1), ("passive", 2))),
).setMaxAccess("read-only")
if mibBuilder.loadTexts:
    egpNeighMode.setStatus("mandatory")
if mibBuilder.loadTexts:
    egpNeighMode.setDescription(
        "The polling mode of this EGP entity, either passive or active."
    )
egpNeighEventTrigger = MibTableColumn(
    (1, 3, 6, 1, 2, 1, 8, 5, 1, 15),
    Integer32()
    .subtype(subtypeSpec=ConstraintsUnion(SingleValueConstraint(1, 2)))
    .clone(namedValues=NamedValues(("start", 1), ("stop", 2))),
).setMaxAccess("read-write")
if mibBuilder.loadTexts:
    egpNeighEventTrigger.setStatus("mandatory")
if mibBuilder.loadTexts:
    egpNeighEventTrigger.setDescription(
        "A control variable used to trigger operator- initiated Start and Stop events. When read, this variable always returns the most recent value that egpNeighEventTrigger was set to. If it has not been set since the last initialization of the network management subsystem on the node, it returns a value of `stop'. When set, this variable causes a Start or Stop event on the specified neighbor, as specified on pages 8-10 of RFC 904. Briefly, a Start event causes an Idle peer to begin neighbor acquisition and a non-Idle peer to reinitiate neighbor acquisition. A stop event causes a non-Idle peer to return to the Idle state until a Start event occurs, either via egpNeighEventTrigger or otherwise."
    )
egpAs = MibScalar((1, 3, 6, 1, 2, 1, 8, 6), Integer32()).setMaxAccess("read-only")
if mibBuilder.loadTexts:
    egpAs.setStatus("mandatory")
if mibBuilder.loadTexts:
    egpAs.setDescription("The autonomous system number of this EGP entity.")
mibBuilder.export_symbols(
    "RFC1213-MIB",
    ipAdEntReasmMaxSize=ipAdEntReasmMaxSize,
    icmpOutAddrMasks=icmpOutAddrMasks,
    ipRouteNextHop=ipRouteNextHop,
    tcpRtoMax=tcpRtoMax,
    ipOutRequests=ipOutRequests,
    udpNoPorts=udpNoPorts,
    ipNetToMediaIfIndex=ipNetToMediaIfIndex,
    ipNetToMediaTable=ipNetToMediaTable,
    udpTable=udpTable,
    tcpRetransSegs=tcpRetransSegs,
    icmpOutAddrMaskReps=icmpOutAddrMaskReps,
    icmpInEchoReps=icmpInEchoReps,
    ipRouteMetric5=ipRouteMetric5,
    ipNetToMediaNetAddress=ipNetToMediaNetAddress,
    ipAddrTable=ipAddrTable,
    tcpAttemptFails=tcpAttemptFails,
    icmpInDestUnreachs=icmpInDestUnreachs,
    ipAdEntIfIndex=ipAdEntIfIndex,
    egpInErrors=egpInErrors,
    TtcpInSegs=tcpInSegs,
    icmpInAddrMaskReps=icmpInAddrMaskReps,
    egp=egp,
    icmpInSrcQuenchs=icmpInSrcQuenchs,
    icmpInTimestamps=icmpInTimestamps,
    ipOutNoRoutes=ipOutNoRoutes,
    icmpOutTimestampReps=icmpOutTimestampReps,
    udpLocalPort=udpLocalPort,
    ipRouteType=ipRouteType,
    atIfIndex=atIfIndex,
    tcpEstabResets=tcpEstabResets,
    icmpOutTimestamps=icmpOutTimestamps,
    ipAdEntBcastAddr=ipAdEntBcastAddr,
    PhysAddress=PhysAddress,
    mib_2=mib_2,
    atPhysAddress=atPhysAddress,
    icmpInAddrMasks=icmpInAddrMasks,
    ipRouteMask=ipRouteMask,
    ipInHdrErrors=ipInHdrErrors,
    egpNeighInMsgs=egpNeighInMsgs,
    egpNeighAs=egpNeighAs,
    icmpOutErrors=icmpOutErrors,
    icmpOutTimeExcds=icmpOutTimeExcds,
    icmpOutEchoReps=icmpOutEchoReps,
    icmpOutDestUnreachs=icmpOutDestUnreachs,
    ipReasmFails=ipReasmFails,
    egpNeighOutErrMsgs=egpNeighOutErrMsgs,
    egpNeighEntry=egpNeighEntry,
    egpNeighTable=egpNeighTable,
    DisplayString=DisplayString,
    ipRouteIfIndex=ipRouteIfIndex,
    tcpRtoMin=tcpRtoMin,
    icmpInParmProbs=icmpInParmProbs,
    tcpCurrEstab=tcpCurrEstab,
    tcpConnLocalPort=tcpConnLocalPort,
    tcpOutRsts=tcpOutRsts,
    icmpOutEchos=icmpOutEchos,
    ipAdEntAddr=ipAdEntAddr,
    ipRouteInfo=ipRouteInfo,
    tcpConnRemAddress=tcpConnRemAddress,
    ipNetToMediaPhysAddress=ipNetToMediaPhysAddress,
    ipDefaultTTL=ipDefaultTTL,
    ipInUnknownProtos=ipInUnknownProtos,
    ipOutDiscards=ipOutDiscards,
    ipRouteEntry=ipRouteEntry,
    egpInMsgs=egpInMsgs,
    egpNeighIntervalHello=egpNeighIntervalHello,
    ipRouteProto=ipRouteProto,
    icmpOutMsgs=icmpOutMsgs,
    egpNeighStateDowns=egpNeighStateDowns,
    ipRouteAge=ipRouteAge,
    icmpInErrors=icmpInErrors,
    tcpConnTable=tcpConnTable,
    egpNeighInErrMsgs=egpNeighInErrMsgs,
    ipInAddrErrors=ipInAddrErrors,
    tcpOutSegs=tcpOutSegs,
    icmpInTimestampReps=icmpInTimestampReps,
    tcpConnLocalAddress=tcpConnLocalAddress,
    udpOutDatagrams=udpOutDatagrams,
    tcpRtoAlgorithm=tcpRtoAlgorithm,
    ipFragCreates=ipFragCreates,
    tcpPassiveOpens=tcpPassiveOpens,
    ipNetToMediaEntry=ipNetToMediaEntry,
    ipInReceives=ipInReceives,
    ipForwDatagrams=ipForwDatagrams,
    tcpActiveOpens=tcpActiveOpens,
    ipFragOKs=ipFragOKs,
    ipAddrEntry=ipAddrEntry,
    ipRouteDest=ipRouteDest,
    udpInDatagrams=udpInDatagrams,
    egpOutErrors=egpOutErrors,
    ipRouteMetric1=ipRouteMetric1,
    ipAdEntNetMask=ipAdEntNetMask,
    tcpConnEntry=tcpConnEntry,
    tcpConnRemPort=tcpConnRemPort,
    ipReasmTimeout=ipReasmTimeout,
    udpInErrors=udpInErrors,
    udpEntry=udpEntry,
    egpNeighState=egpNeighState,
    ipReasmReqds=ipReasmReqds,
    egpNeighInErrs=egpNeighInErrs,
    tcpInErrs=tcpInErrs,
    egpNeighAddr=egpNeighAddr,
    ipInDelivers=ipInDelivers,
    udpLocalAddress=udpLocalAddress,
    icmpOutRedirects=icmpOutRedirects,
    icmpInRedirects=icmpInRedirects,
    ipReasmOKs=ipReasmOKs,
    egpAs=egpAs,
    egpOutMsgs=egpOutMsgs,
    ipRouteMetric3=ipRouteMetric3,
    icmpInMsgs=icmpInMsgs,
    icmpOutParmProbs=icmpOutParmProbs,
    ipRouteMetric2=ipRouteMetric2,
    atTable=atTable,
    egpNeighEventTrigger=egpNeighEventTrigger,
    ipNetToMediaType=ipNetToMediaType,
    icmpOutSrcQuenchs=icmpOutSrcQuenchs,
    icmpInTimeExcds=icmpInTimeExcds,
    icmpInEchos=icmpInEchos,
    egpNeighStateUps=egpNeighStateUps,
    atNetAddress=atNetAddress,
    egpNeighOutMsgs=egpNeighOutMsgs,
    ipRouteTable=ipRouteTable,
    tcpConnState=tcpConnState,
    tcpMaxConn=tcpMaxConn,
    ipForwarding=ipForwarding,
    atEntry=atEntry,
    ipRoutingDiscards=ipRoutingDiscards,
    ipRouteMetric4=ipRouteMetric4,
    egpNeighIntervalPoll=egpNeighIntervalPoll,
    ipFragFails=ipFragFails,
    egpNeighOutErrs=egpNeighOutErrs,
    at=at,
    ipInDiscards=ipInDiscards,
    egpNeighMode=egpNeighMode,
)
