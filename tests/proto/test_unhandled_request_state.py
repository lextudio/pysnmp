"""Regression test for the state kept of SNMPv1/v2c requests nobody handles.

Without an application registered for a request's PDU type, e.g. a GET or an
INFORM request reaching a notification receiver, the message dispatcher asks
the message processing model to report an unknownPDUHandlers error. For
SNMPv1/v2c, ``SnmpV1MessageProcessingModel.prepare_response_message`` always
discards such reports (RFC 3412 §7.1.3b), but it didn't release the state the
security model keeps of the request, unlike its SNMPv3 counterpart. So each
such request with a valid community stayed in the cache of the
community-based security model forever.
"""

from pyasn1.codec.ber import encoder
import pytest

from pysnmp.entity import config, engine
from pysnmp.proto import api

TRANSPORT_DOMAIN = (1, 3, 6, 1, 6, 1, 1)
TRANSPORT_ADDRESS = ("127.0.0.1", 162)


def _build_request(version, pdu_type) -> bytes:
    """A request of the given type from the "public" community."""
    pMod = api.PROTOCOL_MODULES[version]  # noqa: N806
    pdu = getattr(pMod, pdu_type)()
    pMod.apiPDU.set_defaults(pdu)
    message = pMod.Message()
    pMod.apiMessage.set_defaults(message)
    pMod.apiMessage.set_community(message, "public")
    pMod.apiMessage.set_pdu(message, pdu)
    return encoder.encode(message)


@pytest.mark.parametrize(
    "version, pdu_type",
    [
        (api.SNMP_VERSION_1, "GetRequestPDU"),
        (api.SNMP_VERSION_1, "SetRequestPDU"),
        (api.SNMP_VERSION_2C, "GetRequestPDU"),
        (api.SNMP_VERSION_2C, "GetNextRequestPDU"),
        (api.SNMP_VERSION_2C, "GetBulkRequestPDU"),
        (api.SNMP_VERSION_2C, "SetRequestPDU"),
        (api.SNMP_VERSION_2C, "InformRequestPDU"),
    ],
)
def test_unhandled_request_releases_security_model_state(version, pdu_type):
    snmp_engine = engine.SnmpEngine()
    config.add_v1_system(snmp_engine, "my-area", "public")

    snmp_engine.message_dispatcher.receive_message(
        snmp_engine,
        TRANSPORT_DOMAIN,
        TRANSPORT_ADDRESS,
        _build_request(version, pdu_type),
    )

    for security_model in snmp_engine.security_models.values():
        assert security_model._cache.is_empty()
