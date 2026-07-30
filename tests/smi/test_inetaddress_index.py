import pytest
from pathlib import Path

from pysnmp.smi import builder


def _load_mib_builder():
    mibBuilder = builder.MibBuilder()
    mibBuilder.loadTexts = True
    mibBuilder.add_mib_sources(
        builder.DirMibSource(
            Path(__file__).resolve().parents[2] / "pysnmp" / "smi" / "mibs"
        )
    )
    mibBuilder.load_modules("INET-ADDRESS-MIB")
    return mibBuilder


def _make_inet_address_row(mibBuilder):
    (MibTableRow, MibTableColumn) = mibBuilder.import_symbols(
        "SNMPv2-SMI", "MibTableRow", "MibTableColumn"
    )
    (InetAddressType, InetAddress) = mibBuilder.import_symbols(
        "INET-ADDRESS-MIB", "InetAddressType", "InetAddress"
    )

    inetAddressTypeColumn = MibTableColumn(
        (1, 3, 6, 1, 2, 1, 4, 34, 1, 1), InetAddressType()
    )
    inetAddressColumn = MibTableColumn((1, 3, 6, 1, 2, 1, 4, 34, 1, 2), InetAddress())
    mibBuilder.export_symbols(
        "TEST-INET-ADDRESS",
        inetAddressType=inetAddressTypeColumn,
        inetAddress=inetAddressColumn,
    )

    row = MibTableRow((1, 3, 6, 1, 2, 1, 4, 34, 1))
    row.indexNames = (
        (False, "TEST-INET-ADDRESS", "inetAddressType"),
        (False, "TEST-INET-ADDRESS", "inetAddress"),
    )
    return row


@pytest.mark.parametrize(
    "inst_id, expected_type, expected_address",
    [
        ((1, 4, 0, 0, 0, 0), "ipv4", "0.0.0.0"),
        (
            (
                2,
                16,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                1,
            ),
            "ipv6",
            "00:00:00:00:00:00:00:01",
        ),
    ],
)
def test_inetaddress_length_prefixed_index_is_parsed_correctly(
    inst_id, expected_type, expected_address
):
    mibBuilder = _load_mib_builder()
    row = _make_inet_address_row(mibBuilder)

    indices = row.getIndicesFromInstId(inst_id)

    assert indices[0].prettyPrint() == expected_type
    assert indices[1].prettyPrint() == expected_address


def _make_dual_inet_address_row(mibBuilder):
    """Build a row shaped like inetCidrRouteEntry, which indexes on *two*
    InetAddressType/InetAddress pairs (dest and next hop).
    """
    (MibTableRow, MibTableColumn) = mibBuilder.import_symbols(
        "SNMPv2-SMI", "MibTableRow", "MibTableColumn"
    )
    (InetAddressType, InetAddress) = mibBuilder.import_symbols(
        "INET-ADDRESS-MIB", "InetAddressType", "InetAddress"
    )
    (Integer32,) = mibBuilder.import_symbols("SNMPv2-SMI", "Integer32")
    from pyasn1.type.univ import ObjectIdentifier

    base = (1, 3, 6, 1, 2, 1, 4, 24, 7, 1)
    columns = {
        "cidrRouteDestType": MibTableColumn(base + (1,), InetAddressType()),
        "cidrRouteDest": MibTableColumn(base + (2,), InetAddress()),
        "cidrRoutePfxLen": MibTableColumn(base + (3,), Integer32()),
        "cidrRoutePolicy": MibTableColumn(base + (4,), ObjectIdentifier()),
        "cidrRouteNextHopType": MibTableColumn(base + (5,), InetAddressType()),
        "cidrRouteNextHop": MibTableColumn(base + (6,), InetAddress()),
    }
    mibBuilder.export_symbols("TEST-INET-CIDR-ROUTE", **columns)

    row = MibTableRow(base)
    row.indexNames = tuple((False, "TEST-INET-CIDR-ROUTE", name) for name in columns)
    return row


def test_inetaddress_unknown_type_decodes_as_zero_length_address():
    """Regression test for issue #247.

    An InetAddressType of unknown(0) has no INET-ADDRESS-MIB textual convention,
    because the paired address is always zero-length. The type lookup must not
    treat that as "wrong index column" and scan past it, or a row with two
    InetAddressType columns decodes the next hop against the *destination* type.
    """
    mibBuilder = _load_mib_builder()
    row = _make_dual_inet_address_row(mibBuilder)

    # ipv6 destination ff00::/8, next hop type unknown(0) with an empty address.
    inst_id = (
        2,
        16,
        255,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        8,
        2,
        0,
        0,
        0,
        0,
    )

    indices = row.getIndicesFromInstId(inst_id)

    assert len(indices) == 6
    assert indices[0].prettyPrint() == "ipv6"
    assert indices[1].prettyPrint() == "ff00:00:00:00:00:00:00:00"
    assert indices[2].prettyPrint() == "8"
    assert indices[4].prettyPrint() == "unknown"
    assert indices[5].prettyPrint() == ""
    assert len(indices[5]) == 0


def test_inetaddress_unknown_type_encodes_back_to_zero_length_prefix():
    """The encode path must be symmetric: unknown(0) emits just a 0 length."""
    mibBuilder = _load_mib_builder()
    row = _make_dual_inet_address_row(mibBuilder)
    (InetAddressType, InetAddress) = mibBuilder.import_symbols(
        "INET-ADDRESS-MIB", "InetAddressType", "InetAddress"
    )
    (Integer32,) = mibBuilder.import_symbols("SNMPv2-SMI", "Integer32")
    from pyasn1.type.univ import ObjectIdentifier

    parent_indices = [
        InetAddressType(2),  # destination type: ipv6
        InetAddress(""),
        Integer32(8),
        ObjectIdentifier("0.0"),
        InetAddressType(0),  # next hop type: unknown -- the nearest one
    ]

    encoded = InetAddress("").clone_as_name(False, row, parent_indices)

    assert encoded == (0,)
