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


# ---------------------------------------------------------------------------
# Tests for InetAddress without a preceding InetAddressType in the INDEX
# (regression for etingof/pysnmp#305 / lextudio/pysnmp#305).
# Non-compliant MIBs such as MPLS-VPN-MIB omit InetAddressType from the
# index, so pysnmp must infer the address type from the byte length.
# ---------------------------------------------------------------------------


def _make_inet_address_only_row(mibBuilder):
    """Row whose INDEX contains only InetAddress (no InetAddressType)."""
    (MibTableRow, MibTableColumn) = mibBuilder.import_symbols(
        "SNMPv2-SMI", "MibTableRow", "MibTableColumn"
    )
    (InetAddress,) = mibBuilder.import_symbols("INET-ADDRESS-MIB", "InetAddress")

    inetAddressColumn = MibTableColumn((1, 3, 6, 1, 2, 1, 99, 1, 1), InetAddress())
    mibBuilder.export_symbols(
        "TEST-INET-ADDRESS-ONLY",
        inetAddressOnly=inetAddressColumn,
    )

    row = MibTableRow((1, 3, 6, 1, 2, 1, 99, 1))
    row.indexNames = ((False, "TEST-INET-ADDRESS-ONLY", "inetAddressOnly"),)
    return row


@pytest.mark.parametrize(
    "addr_bytes, expected_display",
    [
        # IPv4: 4 bytes
        ((192, 0, 2, 1), "192.0.2.1"),
        # IPv6: 16 bytes (::1)
        ((0,) * 15 + (1,), "00:00:00:00:00:00:00:01"),
    ],
)
def test_inetaddress_no_type_index_clone_from_name(addr_bytes, expected_display):
    """
    etingof/pysnmp#305: InetAddress.clone_from_name must not raise SmiError
    when no InetAddressType precedes it in the INDEX.  Address type is inferred
    from byte length: 4 → ipv4, 16 → ipv6.
    """
    mibBuilder = _load_mib_builder()
    row = _make_inet_address_only_row(mibBuilder)

    length = len(addr_bytes)
    inst_id = (length,) + tuple(addr_bytes)

    indices = row.getIndicesFromInstId(inst_id)
    assert indices[0].prettyPrint() == expected_display


@pytest.mark.parametrize(
    "addr_bytes, expected_inst_suffix",
    [
        ((127, 0, 0, 1), (4, 127, 0, 0, 1)),
        ((0,) * 15 + (1,), (16,) + (0,) * 15 + (1,)),
    ],
)
def test_inetaddress_no_type_index_clone_as_name(addr_bytes, expected_inst_suffix):
    """
    etingof/pysnmp#305: InetAddress.clone_as_name must produce a valid OID
    suffix (length-prefixed) when no InetAddressType precedes it in the INDEX.
    """
    mibBuilder = _load_mib_builder()
    (InetAddress,) = mibBuilder.import_symbols("INET-ADDRESS-MIB", "InetAddress")

    addr = InetAddress(hexValue=bytes(addr_bytes).hex())
    result = addr.clone_as_name(impliedFlag=False, parentRow=None, parentIndices=[])
    assert result == expected_inst_suffix
