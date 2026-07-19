from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol

from src.core.types import Platform, MessageDirection, MessageStatus


@dataclass
class Message:
    id: str
    platform: Platform
    direction: MessageDirection
    sender: str
    content: str
    timestamp: datetime
    status: MessageStatus = MessageStatus.PENDING
    metadata: dict = field(default_factory=dict)


class MessageSource(Protocol):
    """Interface each platform adapter must implement."""

    platform: Platform

    async def send(self, message: Message) -> MessageStatus: ...

    async def receive(self) -> list[Message]: ...

    async def parse_webhook(self, raw: dict) -> Message: ...
