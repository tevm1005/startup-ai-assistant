"""Core interfaces and types smoke tests."""

from src.core.types import Platform, MessageDirection, MessageStatus


def test_enums_have_expected_values():
    assert Platform.WHATSAPP.value == "whatsapp"
    assert MessageDirection.INBOUND.value == "inbound"
    assert MessageStatus.PENDING.value == "pending"
