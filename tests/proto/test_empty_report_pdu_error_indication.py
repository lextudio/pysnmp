"""Regression test for the missing errorIndication on empty Report-PDUs.

lextudio/pysnmp#241: ``KeyError: 'errorIndication'``.

A Report-PDU must carry exactly one varbind naming the error (RFC 3412
§7.2.11a). When a non-conformant peer sent one with an empty varbind list,
``prepare_data_elements`` built a ``StatusInformation`` carrying only
``sendPduHandle``. The guard in ``proto/rfc3412.py`` forwards anything with a
``sendPduHandle`` to the command generator, which then did::

    errorIndication = statusInformation["errorIndication"]

and raised ``KeyError`` instead of reporting an error to the caller.

An AST sweep of all 103 ``StatusInformation(...)`` construction sites showed
this was the only one omitting ``errorIndication`` while carrying a
``sendPduHandle``, so fixing it here is sufficient -- no defensive ``.get()``
is needed downstream.

The USM layer is stubbed so the test exercises the real message parsing and
the real Report-PDU branch; only the cryptography, which is not what is under
test, is bypassed.
"""

from pyasn1.codec.ber import encoder
import pytest

from pysnmp.entity import config, engine
from pysnmp.proto import api, error, rfc1905
from pysnmp.proto.mpmod import rfc3412
from pysnmp.proto.secmod.rfc3414.service import UsmSecurityParameters

pMod = api.PROTOCOL_MODULES[api.SNMP_VERSION_2C]  # noqa: N816

TRANSPORT_DOMAIN = (1, 3, 6, 1, 6, 1, 1)
TRANSPORT_ADDRESS = ("127.0.0.1", 161)


class _StubDispatcher:
    """Enough of a transport dispatcher for the engine-ID cache timer."""

    def get_timer_resolution(self):
        return 1.0


def _build_empty_report_pdu(engine_id) -> bytes:
    """A well-formed SNMPv3 Report-PDU whose varbind list is empty."""
    pdu = rfc1905.ReportPDU()
    pMod.apiPDU.set_defaults(pdu)
    pMod.apiPDU.set_request_id(pdu, 0)
    pMod.apiPDU.set_error_status(pdu, 0)
    pMod.apiPDU.set_error_index(pdu, 0)
    pMod.apiPDU.set_varbinds(pdu, [])
    assert pMod.apiPDU.get_varbinds(pdu) == []

    security_parameters = UsmSecurityParameters()
    security_parameters.setComponentByPosition(0, engine_id.syntax.clone())
    security_parameters.setComponentByPosition(1, 0)
    security_parameters.setComponentByPosition(2, 0)
    security_parameters.setComponentByPosition(3, "usr-md5-none")
    security_parameters.setComponentByPosition(4, b"")
    security_parameters.setComponentByPosition(5, b"")

    message = rfc3412.SNMPv3Message()
    message.setComponentByPosition(0, 3)
    message.setComponentByPosition(1)
    global_data = message.getComponentByPosition(1)
    global_data.setComponentByPosition(0, 1)
    global_data.setComponentByPosition(1, 65507)
    global_data.setComponentByPosition(2, b"\x05")  # noAuthNoPriv, reportable
    global_data.setComponentByPosition(3, 3)  # USM
    message.setComponentByPosition(2, encoder.encode(security_parameters))

    scoped_pdu = rfc3412.ScopedPDU()
    scoped_pdu.setComponentByPosition(0, engine_id.syntax.clone())
    scoped_pdu.setComponentByPosition(1, b"")
    scoped_pdu.getComponentByPosition(2).setComponentByName("report", pdu)

    scoped_pdu_data = rfc3412.ScopedPduData()
    scoped_pdu_data.setComponentByName("plaintext", scoped_pdu)
    message.setComponentByPosition(3, scoped_pdu_data)

    return encoder.encode(message)


@pytest.fixture
def snmp_engine():
    eng = engine.SnmpEngine()
    config.add_v3_user(eng, "usr-md5-none", config.USM_AUTH_HMAC96_MD5, "authkey1")
    (engine_id,) = eng.get_mib_builder().import_symbols(
        "__SNMP-FRAMEWORK-MIB", "snmpEngineID"
    )
    return eng, engine_id


def _run_with_stubbed_security(eng, engine_id):
    """Drive prepare_data_elements with USM stubbed to succeed."""
    eng.transport_dispatcher = _StubDispatcher()

    wire = _build_empty_report_pdu(engine_id)

    # Decode the scoped PDU the stub will hand back, so the real parsing and
    # the real Report-PDU branch both run.
    from pyasn1.codec.ber import decoder

    decoded, _ = decoder.decode(wire, asn1Spec=rfc3412.SNMPv3Message())
    scoped_pdu = decoded.getComponentByPosition(3).getComponentByName("plaintext")

    security_model = eng.security_models[3]

    def fake_process_incoming_message(*args, **kwargs):
        return (
            engine_id.syntax.clone(),
            "usr-md5-none",
            scoped_pdu,
            65507,
            "sec-ref",
        )

    def fake_release_state_information(*args, **kwargs):
        return None

    original_process = security_model.process_incoming_message
    original_release = security_model.release_state_information
    security_model.process_incoming_message = fake_process_incoming_message
    security_model.release_state_information = fake_release_state_information
    try:
        mpmod = rfc3412.SnmpV3MessageProcessingModel()

        # A request is in flight, so the Report-PDU's msgID resolves and the
        # Report-PDU branch is reached. Without this the message processing
        # model bails out earlier with errind.dataMismatch.
        send_pdu_handle = 4242
        mpmod._cache.push_by_message_id(  # noqa: SLF001
            1, sendPduHandle=send_pdu_handle
        )

        with pytest.raises(error.StatusInformation) as exc_info:
            mpmod.prepare_data_elements(eng, TRANSPORT_DOMAIN, TRANSPORT_ADDRESS, wire)
        return exc_info.value
    finally:
        security_model.process_incoming_message = original_process
        security_model.release_state_information = original_release


def test_empty_report_pdu_yields_error_indication(snmp_engine):
    """The raised StatusInformation must carry an errorIndication."""
    status_information = _run_with_stubbed_security(*snmp_engine)

    assert "errorIndication" in status_information, (
        "StatusInformation lacks errorIndication: %s" % status_information
    )


def test_empty_report_pdu_keeps_send_pdu_handle(snmp_engine):
    """The sendPduHandle must survive, or the request is never retried."""
    status_information = _run_with_stubbed_security(*snmp_engine)

    assert "sendPduHandle" in status_information


def test_cmdgen_access_does_not_raise_key_error(snmp_engine):
    """The exact access that produced the #241 KeyError must now succeed."""
    status_information = _run_with_stubbed_security(*snmp_engine)

    # this is what entity/rfc3413/cmdgen.py does
    error_indication = status_information["errorIndication"]

    assert error_indication is not None
    assert not isinstance(error_indication, str) or error_indication
