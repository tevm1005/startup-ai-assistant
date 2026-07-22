from __future__ import annotations

import os
from datetime import datetime

import httpx

from src.core.interfaces import Message, MessageSource, MessageStatus
from src.core.types import Platform, MessageDirection, MessageDirection

WHATSAPP_API_BASE = "https://graph.facebook.com/v22.0"


class WhatsAppAdapter(MessageSource):
    platform = Platform.WHATSAPP

    def __init__(self) -> None:
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
        self.access_token = os.getenv("WHATSAPP_ACCESS_TOKEN", "")
        self.verify_token = os.getenv("WHATSAPP_WEBHOOK_VERIFY_TOKEN", "")

    async def send(self, message: Message) -> MessageStatus:
        if not self.phone_number_id or not self.access_token:
            return MessageStatus.FAILED
        url = f"{WHATSAPP_API_BASE}/{self.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": message.sender,
            "type": "text",
            "text": {"body": message.content},
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.is_success:
                return MessageStatus.SENT
            return MessageStatus.FAILED

    async def receive(self) -> list[Message]:
        return []

    async def parse_webhook(self, raw: dict) -> Message:
        entry = raw["entry"][0]
        change = entry["changes"][0]
        value = change["value"]
        msg = value["messages"][0]

        return Message(
            id=msg["id"],
            platform=Platform.WHATSAPP,
            direction=MessageDirection.INBOUND,
            sender=msg["from"],
            content=msg["text"]["body"],
            timestamp=datetime.fromtimestamp(int(msg["timestamp"])),
        )
