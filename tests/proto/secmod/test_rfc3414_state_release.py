"""Security state must not outlive a request the USM rejects without a Report.

``process_incoming_message`` caches a ``securityStateReference`` for each
request. When it fails with a ``StatusInformation`` that carries no
``oid`` the message processing model re-raises it without producing a Report,
so nothing else ever releases that state unless the security model does.
When the failure does carry an ``oid`` a Report is generated and the state is
released later by ``generate_response_message``; it must still be there.
"""

import pytest
from pyasn1.codec.ber import encoder

from pysnmp.entity import config, engine
from pysnmp.proto import errind, error
from pysnmp.proto.api import v2c
from pysnmp.proto.mpmod import rfc3412
from pysnmp.proto.secmod.rfc3414 import service

USER = b"usr-none"


def _engine_with_user():
    snmp_engine = engine.SnmpEngine()
    config.add_v3_user(snmp_engine, USER.decode())
    return snmp_engine


def _local_engine_id(snmp_engine):
    (engine_id,) = snmp_engine.get_mib_builder().import_symbols(
        "__SNMP-FRAMEWORK-MIB", "snmpEngineID"
    )
    return engine_id.syntax


def _message(scoped_pdu=None, encrypted_pdu=None):
    message = rfc3412.SNMPv3Message()
    message.setComponentByPosition(0, 3)
    message.setComponentByPosition(1)
    header = message.getComponentByPosition(1)
    header.setComponentByPosition(0, 1)
    header.setComponentByPosition(1, 65507)
    header.setComponentByPosition(2, b"\x04")
    header.setComponentByPosition(3, 3)
    scoped_pdu_data = message.getComponentByPosition(3)
    if scoped_pdu is not None:
        scoped_pdu_data.setComponentByPosition(0, scoped_pdu)
    else:
        scoped_pdu_data.setComponentByPosition(1, encrypted_pdu)
    return message


def _scoped_pdu(engine_id):
    request = v2c.GetRequestPDU()
    v2c.apiPDU.set_defaults(request)
    v2c.apiPDU.set_varbinds(request, [((1, 3, 6, 1, 2, 1, 1, 1, 0), None)])
    scoped_pdu = rfc3412.ScopedPDU()
    scoped_pdu.setComponentByPosition(0, engine_id)
    scoped_pdu.setComponentByPosition(1, b"")
    scoped_pdu.getComponentByPosition(2).setComponentByPosition(0, request)
    return scoped_pdu


def _process(snmp_engine, message, engine_id, user=USER, security_level=1):
    security_parameters = service.UsmSecurityParameters()
    security_parameters.setComponentByPosition(0, engine_id)
    security_parameters.setComponentByPosition(1, 0)
    security_parameters.setComponentByPosition(2, 0)
    security_parameters.setComponentByPosition(3, user)
    security_parameters.setComponentByPosition(4, b"")
    security_parameters.setComponentByPosition(5, b"")
    encoded = encoder.encode(security_parameters)
    message.setComponentByPosition(2, encoded)

    return snmp_engine.security_models[3].process_incoming_message(
        snmp_engine,
        3,
        65507,
        encoded,
        3,
        security_level,
        encoder.encode(message),
        message,
    )


def _cache(snmp_engine):
    return snmp_engine.security_models[3]._cache


def test_undiscoverable_engine_id_releases_state():
    snmp_engine = _engine_with_user()
    (discoverable,) = snmp_engine.get_mib_builder().import_symbols(
        "__PYSNMP-USM-MIB", "pysnmpUsmDiscoverable"
    )
    discoverable.syntax = discoverable.syntax.clone(0)
    message = _message(scoped_pdu=_scoped_pdu(_local_engine_id(snmp_engine)))

    with pytest.raises(error.StatusInformation) as raised:
        _process(snmp_engine, message, b"")

    assert "oid" not in raised.value
    assert raised.value["errorIndication"] is errind.unknownEngineID
    assert _cache(snmp_engine).is_empty()


def test_discovery_with_encrypted_pdu_releases_state():
    snmp_engine = _engine_with_user()
    message = _message(encrypted_pdu=b"\x00")

    with pytest.raises(error.StatusInformation) as raised:
        _process(snmp_engine, message, b"")

    assert "oid" not in raised.value
    assert raised.value["errorIndication"] is errind.unknownEngineID
    assert _cache(snmp_engine).is_empty()


def test_reported_failure_keeps_state_for_the_report():
    snmp_engine = _engine_with_user()
    message = _message(scoped_pdu=_scoped_pdu(_local_engine_id(snmp_engine)))

    with pytest.raises(error.StatusInformation) as raised:
        _process(snmp_engine, message, _local_engine_id(snmp_engine), user=b"nobody")

    assert "oid" in raised.value
    assert raised.value["errorIndication"] is errind.unknownSecurityName
    assert not _cache(snmp_engine).is_empty()
    snmp_engine.security_models[3].release_state_information(
        raised.value["securityStateReference"]
    )
    assert _cache(snmp_engine).is_empty()
