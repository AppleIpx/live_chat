import uuid
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID

from fastapi_users_db_sqlalchemy import GUID
from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from live_chat.db.base import Base
from live_chat.db.models.enums import MessageType

if TYPE_CHECKING:
    from live_chat.db.models.chat import Chat  # type: ignore[attr-defined]
    from live_chat.db.models.reaction import Reaction
    from live_chat.db.models.user import User


class BaseMessage(Base):
    """Abstract base class for messages."""

    __abstract__ = True

    id: Mapped[UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    message_type: Mapped[MessageType] = mapped_column(
        Enum(MessageType, inherit_schema=True),
        default=MessageType.TEXT,
    )
    content: Mapped[Optional[str]] = mapped_column(String(5000), nullable=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"))
    chat_id: Mapped[UUID] = mapped_column(ForeignKey("chat.id"))
    file_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    file_path: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    parent_message_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("message.id"),
        nullable=True,
    )


class Message(BaseMessage):
    """Message model."""

    __tablename__ = "message"

    chat: Mapped["Chat"] = relationship(
        back_populates="messages",
        overlaps="deleted_messages",
    )
    user = relationship("User", back_populates="messages")
    reactions: Mapped[List["Reaction"]] = relationship(
        "Reaction",
        back_populates="message",
        cascade="all, delete-orphan",
    )
    parent_message_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("message.id"),
        nullable=True,
        default=None,
    )
    parent_message: Mapped["Message"] = relationship(
        "Message",
        remote_side="Message.id",
        backref="replies",
        foreign_keys=[parent_message_id],
    )
    forwarded_message_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("message.id"),
        nullable=True,
        default=None,
    )
    forwarded_message: Mapped["Message"] = relationship(
        "Message",
        remote_side="Message.id",
        backref="forwarded_by",
        foreign_keys=[forwarded_message_id],
    )

    def __str__(self) -> str:
        return f"Message from {self.user_id} - {self.chat_id} - {self.created_at}"


class DeletedMessage(BaseMessage):
    """Deleted Message model."""

    __tablename__ = "deleted_message"

    original_message_id = mapped_column(GUID)
    chat: Mapped["Chat"] = relationship(
        back_populates="deleted_messages",
        overlaps="messages",
    )
    user = relationship("User", back_populates="deleted_messages")

    def __str__(self) -> str:
        return (
            f"Deleted message from {self.user_id} - {self.chat_id} - {self.created_at}"
        )


class DraftMessage(BaseMessage):
    """Draft Message model."""

    __tablename__ = "draft_message"

    chat: Mapped["Chat"] = relationship("Chat", back_populates="draft_messages")
    user: Mapped["User"] = relationship("User", back_populates="draft_messages")

    def __str__(self) -> str:
        return f"Draft by {self.user_id} in chat {self.chat_id}"
