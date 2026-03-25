from unittest import mock

from pysnmp.carrier.asyncio.dgram import udp6
from pysnmp.entity import config
from pysnmp.entity.engine import SnmpEngine
from pysnmp.entity.rfc3413 import config as rfc3413_config


class _FakeAddress(tuple):
    def set_local_address(self, addr):
        self.local_address = addr
        return self

    def get_local_address(self):
        return self.local_address


def test_add_target_address_stores_ipv6_zone_addresses():
    with SnmpEngine() as snmpEngine:
        config.add_target_address(
            snmpEngine,
            "scoped",
            udp6.DOMAIN_NAME,
            ("fe80::1", 161, 0, 3),
            "params",
        )

        mibBuilder = snmpEngine.get_mib_builder()
        (snmpTargetAddrEntry, snmpTargetAddrTAddress) = mibBuilder.import_symbols(
            "SNMP-TARGET-MIB", "snmpTargetAddrEntry", "snmpTargetAddrTAddress"
        )
        (snmpSourceAddrTAddress,) = mibBuilder.import_symbols(
            "PYSNMP-SOURCE-MIB", "snmpSourceAddrTAddress"
        )

        tblIdx = snmpTargetAddrEntry.getInstIdFromIndices("scoped")
        targetAddress = snmpTargetAddrTAddress.getNode(
            snmpTargetAddrTAddress.name + tblIdx
        ).syntax
        sourceAddress = snmpSourceAddrTAddress.getNode(
            snmpSourceAddrTAddress.name + tblIdx
        ).syntax

        assert len(targetAddress.asOctets()) == 22
        assert len(sourceAddress.asOctets()) == 22


def test_get_target_address_preserves_ipv6_zone_id():
    with SnmpEngine() as snmpEngine:
        config.add_target_address(
            snmpEngine,
            "scoped",
            udp6.DOMAIN_NAME,
            ("fe80::1", 161, 0, 3),
            "params",
            sourceAddress=("fe80::2", 162, 0, 7),
        )

        snmpEngine.transport_dispatcher = mock.Mock()
        snmpEngine.transport_dispatcher.get_transport.return_value = mock.Mock(
            ADDRESS_TYPE=_FakeAddress
        )

        _, addr, _, _, _ = rfc3413_config.get_target_address(snmpEngine, "scoped")

        assert tuple(addr) == ("fe80::1", 161, 0, 3)
        assert tuple(addr.get_local_address()) == ("fe80::2", 162, 0, 7)
