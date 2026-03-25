from pysnmp.smi.rfc1902 import NotificationType, ObjectIdentity, ObjectType


def test_is_fully_resolved_returns_bool_for_all_wrappers():
    object_identity = ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)
    object_type = ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0))
    notification_type = NotificationType(ObjectIdentity("IF-MIB", "linkDown"))

    assert object_identity.is_fully_resolved() is False
    assert isinstance(object_identity.is_fully_resolved(), bool)

    assert object_type.is_fully_resolved() is False
    assert isinstance(object_type.is_fully_resolved(), bool)

    assert notification_type.is_fully_resolved() is False
    assert isinstance(notification_type.is_fully_resolved(), bool)
