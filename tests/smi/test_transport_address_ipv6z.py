from pysnmp.entity.engine import SnmpEngine


def test_transport_address_ipv6z_round_trips_socket_tuple():
    with SnmpEngine() as snmpEngine:
        mibBuilder = snmpEngine.get_mib_builder()
        (TransportAddressIPv6z,) = mibBuilder.import_symbols(
            "TRANSPORT-ADDRESS-MIB", "TransportAddressIPv6z"
        )

        assert tuple(TransportAddressIPv6z(("fe80::1", 161, 0, 513))) == (
            "fe80::1",
            161,
            0,
            513,
        )
