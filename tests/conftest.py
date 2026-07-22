from datetime import datetime

import pytest


@pytest.fixture
def sample_message():
    from src.core.interfaces import Message
    from src.core.types import Platform, MessageDirection, MessageStatus

    return Message(
        id="msg_1",
        platform=Platform.WHATSAPP,
        direction=MessageDirection.INBOUND,
        sender="+5511999999999",
        content="Qual é o preço do plano básico?",
        timestamp=datetime.now(),
    )
