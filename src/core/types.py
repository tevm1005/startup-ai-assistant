from enum import StrEnum, auto


class Platform(StrEnum):
    WHATSAPP = auto()
    FACEBOOK = auto()
    INSTAGRAM = auto()
    TIKTOK = auto()


class MessageDirection(StrEnum):
    INBOUND = auto()
    OUTBOUND = auto()


class MessageStatus(StrEnum):
    PENDING = auto()
    SENT = auto()
    DELIVERED = auto()
    READ = auto()
    FAILED = auto()
