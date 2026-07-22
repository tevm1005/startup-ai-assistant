"""Database models for knowledge base and conversations."""

import datetime
import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.types import Platform, MessageDirection, MessageStatus
from src.database.connection import Base


class KnowledgeEntry(Base):
    __tablename__ = "knowledge_embeddings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    extra_metadata: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)
    embedding: Mapped[list[float]] = mapped_column(Vector(768), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform: Mapped[Platform] = mapped_column(String(20), nullable=False)
    external_id: Mapped[str] = mapped_column(String(255), nullable=False)  # platform thread ID
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    messages: Mapped[list["MessageLog"]] = relationship(back_populates="conversation")


class MessageLog(Base):
    __tablename__ = "message_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False
    )
    direction: Mapped[MessageDirection] = mapped_column(String(10), nullable=False)
    sender: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[MessageStatus] = mapped_column(String(20), default=MessageStatus.PENDING)
    extra_metadata: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)
    timestamp: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    conversation: Mapped[Conversation] = relationship(back_populates="messages")
