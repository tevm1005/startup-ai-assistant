"""Tests for WhatsAppAdapter."""

import pytest

from src.core.types import Platform, MessageDirection


@pytest.mark.asyncio
async def test_parse_webhook():
    from src.platforms.whatsapp.adapter import WhatsAppAdapter

    adapter = WhatsAppAdapter()
    payload = {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messages": [
                                {
                                    "id": "wamid.123",
                                    "from": "+5511999999999",
                                    "text": {"body": "Qual é o preço?"},
                                    "timestamp": "1700000000",
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }

    msg = await adapter.parse_webhook(payload)

    assert msg.id == "wamid.123"
    assert msg.platform == Platform.WHATSAPP
    assert msg.direction == MessageDirection.INBOUND
    assert msg.sender == "+5511999999999"
    assert msg.content == "Qual é o preço?"
    assert msg.status.value == "pending"
    assert msg.timestamp is not None


@pytest.mark.asyncio
async def test_send_returns_failed_without_credentials():
    from src.platforms.whatsapp.adapter import WhatsAppAdapter
    from src.core.interfaces import Message
    from src.core.types import Platform, MessageDirection, MessageStatus

    adapter = WhatsAppAdapter()
    msg = Message(
        id="test",
        platform=Platform.WHATSAPP,
        direction=MessageDirection.OUTBOUND,
        sender="+5511999999999",
        content="hello",
        timestamp=__import__("datetime").datetime.now(),
    )

    status = await adapter.send(msg)
    assert status == MessageStatus.FAILED


@pytest.mark.asyncio
async def test_receive_returns_empty():
    from src.platforms.whatsapp.adapter import WhatsAppAdapter

    adapter = WhatsAppAdapter()
    msgs = await adapter.receive()
    assert msgs == []


def test_platform_is_whatsapp():
    from src.platforms.whatsapp.adapter import WhatsAppAdapter

    assert WhatsAppAdapter.platform == Platform.WHATSAPP
