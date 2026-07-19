"""WhatsApp Business API adapter."""

from src.core.interfaces import Message, MessageSource, MessageStatus
from src.core.types import Platform


class WhatsAppAdapter(MessageSource):
    platform = Platform.WHATSAPP

    async def send(self, message: Message) -> MessageStatus:
        ...

    async def receive(self) -> list[Message]:
        ...

    async def parse_webhook(self, raw: dict) -> Message:
        ...
