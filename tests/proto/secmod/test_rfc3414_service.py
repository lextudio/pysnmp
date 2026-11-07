from pyasn1.codec.ber import encoder
import pytest

from pysnmp.entity import config, engine
from pysnmp.proto import errind, error
from pysnmp.proto.api import v2c
from pysnmp.proto.mpmod import rfc3412
from pysnmp.proto.secmod.rfc3414 import service


def test_authenticated_message_with_empty_authentication_parameters_is_rejected():
    snmp_engine = engine.SnmpEngine()
    config.add_v3_user(
        snmp_engine, "usr-sha-none", config.USM_AUTH_HMAC96_SHA, "authkey1"
    )

    mib_builder = snmp_engine.get_mib_builder()
    (snmp_engine_id,) = mib_builder.import_symbols(
        "__SNMP-FRAMEWORK-MIB", "snmpEngineID"
    )
    snmp_engine_boots, snmp_engine_time = mib_builder.import_symbols(
        "__SNMP-FRAMEWORK-MIB", "snmpEngineBoots", "snmpEngineTime"
    )

    request = v2c.GetRequestPDU()
    v2c.apiPDU.set_defaults(request)
    v2c.apiPDU.set_varbinds(request, [((1, 3, 6, 1, 2, 1, 1, 1, 0), None)])

    scoped_pdu = rfc3412.ScopedPDU()
    scoped_pdu.setComponentByPosition(0, snmp_engine_id.syntax)
    scoped_pdu.setComponentByPosition(1, b"")
    scoped_pdu.getComponentByPosition(2).setComponentByPosition(0, request)

    message = rfc3412.SNMPv3Message()
    message.setComponentByPosition(0, 3)
    message.setComponentByPosition(1)
    header = message.getComponentByPosition(1)
    header.setComponentByPosition(0, 1)
    header.setComponentByPosition(1, 65507)
    header.setComponentByPosition(2, b"\x05")
    header.setComponentByPosition(3, 3)
    message.getComponentByPosition(3).setComponentByPosition(0, scoped_pdu)

    security_parameters = service.UsmSecurityParameters()
    security_parameters.setComponentByPosition(0, snmp_engine_id.syntax)
    security_parameters.setComponentByPosition(1, int(snmp_engine_boots.syntax))
    security_parameters.setComponentByPosition(2, int(snmp_engine_time.syntax))
    security_parameters.setComponentByPosition(3, b"usr-sha-none")
    security_parameters.setComponentByPosition(4, b"")
    security_parameters.setComponentByPosition(5, b"")
    encoded_security_parameters = encoder.encode(security_parameters)
    message.setComponentByPosition(2, encoded_security_parameters)

    with pytest.raises(error.StatusInformation) as raised:
        snmp_engine.security_models[3].process_incoming_message(
            snmp_engine,
            3,
            65507,
            encoded_security_parameters,
            3,
            2,
            encoder.encode(message),
            message,
        )

    assert raised.value["errorIndication"] is errind.authenticationFailure


@pytest.mark.parametrize(
    "pdu_type, encrypted, msg_flags, expected",
    [
        (v2c.GetRequestPDU, False, 0x05, errind.unknownEngineID),
        (v2c.GetRequestPDU, True, 0x07, errind.unknownEngineID),
        (v2c.SNMPv2TrapPDU, False, 0x01, errind.unknownSecurityName),
        (v2c.SNMPv2TrapPDU, True, 0x03, errind.unknownSecurityName),
    ],
)
def test_foreign_engine_id_is_reported_only_when_authoritative(
    pdu_type, encrypted, msg_flags, expected
):
    snmp_engine = engine.SnmpEngine()
    config.add_v3_user(
        snmp_engine, "usr-sha-none", config.USM_AUTH_HMAC96_SHA, "authkey1"
    )
    foreign_engine_id = bytes.fromhex("8000000001aa")

    pdu = pdu_type()
    v2c.apiPDU.set_defaults(pdu)

    scoped_pdu = rfc3412.ScopedPDU()
    scoped_pdu.setComponentByPosition(0, foreign_engine_id)
    scoped_pdu.setComponentByPosition(1, b"")
    scoped_pdu.getComponentByPosition(2).setComponentByType(pdu.tagSet, pdu)

    message = rfc3412.SNMPv3Message()
    message.setComponentByPosition(0, 3)
    message.setComponentByPosition(1)
    header = message.getComponentByPosition(1)
    header.setComponentByPosition(0, 1)
    header.setComponentByPosition(1, 65507)
    header.setComponentByPosition(2, bytes([msg_flags]))
    header.setComponentByPosition(3, 3)
    if encrypted:
        message.getComponentByPosition(3).setComponentByName("encryptedPDU", bytes(16))
    else:
        message.getComponentByPosition(3).setComponentByPosition(0, scoped_pdu)

    security_parameters = service.UsmSecurityParameters()
    security_parameters.setComponentByPosition(0, foreign_engine_id)
    security_parameters.setComponentByPosition(1, 1)
    security_parameters.setComponentByPosition(2, 1)
    security_parameters.setComponentByPosition(3, b"usr-sha-none")
    security_parameters.setComponentByPosition(4, bytes(12))
    security_parameters.setComponentByPosition(5, bytes(8) if encrypted else b"")
    encoded_security_parameters = encoder.encode(security_parameters)
    message.setComponentByPosition(2, encoded_security_parameters)

    with pytest.raises(error.StatusInformation) as raised:
        snmp_engine.security_models[3].process_incoming_message(
            snmp_engine,
            3,
            65507,
            encoded_security_parameters,
            3,
            3 if encrypted else 2,
            encoder.encode(message),
            message,
        )

    assert raised.value["errorIndication"] is expected
    if expected is errind.unknownEngineID:
        assert raised.value["oid"] == (1, 3, 6, 1, 6, 3, 15, 1, 1, 4, 0)
        assert raised.value["securityLevel"] == 1  # noAuthNoPriv
