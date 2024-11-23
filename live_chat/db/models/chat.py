# type: ignore
import uuid
from datetime import datetime
from typing import List

from fastapi_users_db_sqlalchemy import GUID, UUID_ID, SQLAlchemyBaseUserTableUUID
from sqlalchemy import (
    UUID,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    String,
    Table,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from live_chat.db.base import Base
from live_chat.db.meta import meta
from live_chat.db.models.enums import ChatType, MessageType
from live_chat.db.utils import RemoveBaseFieldsMixin

chat_participant = Table(
    "chat_participant",
    meta,
    Column("user_id", UUID, ForeignKey("user.id"), primary_key=True),
    Column("chat_id", UUID, ForeignKey("chat.id"), primary_key=True),
)


class Message(Base):
    """Message model."""

    __tablename__ = "message"

    id: Mapped[UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    message_type: Mapped[str] = mapped_column(
        Enum(MessageType, inherit_schema=True),
        default=MessageType.TEXT,
    )
    content: Mapped[str] = mapped_column(String(5000))
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"))
    chat_id: Mapped[UUID] = mapped_column(ForeignKey("chat.id"))

    file_name: Mapped[str] = mapped_column(String(50), nullable=True)
    file_path: Mapped[str] = mapped_column(String(1000), nullable=True)

    chat: Mapped["Chat"] = relationship(back_populates="messages")
    user: Mapped["User"] = relationship(back_populates="messages")

    def __str__(self) -> str:
        return f"Message from {self.user_id} - {self.chat_id} - {self.created_at}"


class Chat(Base):
    """Chat model."""

    __tablename__ = "chat"

    id: Mapped[UUID_ID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    chat_type: Mapped[MessageType] = mapped_column(Enum(ChatType, inherit_schema=True))
    name: Mapped[str] = mapped_column(String(50), nullable=True, default=None)
    image: Mapped[str] = mapped_column(String(1048), nullable=True, default=None)

    users: Mapped[List["User"]] = relationship(
        secondary="chat_participant",
        back_populates="chats",
    )
    messages: Mapped[List[Message]] = relationship(
        back_populates="chat",
        cascade="all,delete",
    )
    read_statuses: Mapped[List["ReadStatus"]] = relationship(
        back_populates="chat",
        cascade="all,delete",
    )

    def __str__(self) -> str:
        return f"{self.chat_type.value.title()} {self.id}"


class ReadStatus(RemoveBaseFieldsMixin, Base):  # type: ignore[misc]
    """Read status model."""

    __tablename__ = "read_status"

    id: Mapped[UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    last_read_message_id: Mapped[UUID] = mapped_column(GUID, nullable=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"))
    chat_id: Mapped[UUID] = mapped_column(ForeignKey("chat.id"))

    chat: Mapped[Chat] = relationship(back_populates="read_statuses")
    user: Mapped["User"] = relationship(back_populates="read_statuses")

    def __str__(self) -> str:
        return f"User: {self.user_id}, Message: {self.last_read_message_id}"


class User(SQLAlchemyBaseUserTableUUID, Base):
    """Represents a user entity."""

    __tablename__ = "user"

    username: Mapped[str] = mapped_column(String(150), unique=True)
    first_name: Mapped[str] = mapped_column(String(150), default="")
    last_name: Mapped[str] = mapped_column(String(150), default="")
    last_login: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    user_image: Mapped[str] = mapped_column(String(1048), nullable=True)

    chats: Mapped[List["Chat"]] = relationship(
        secondary="chat_participant",
        back_populates="users",
    )
    messages: Mapped[List["Message"]] = relationship(
        back_populates="user",
    )
    read_statuses: Mapped[List["ReadStatus"]] = relationship(
        back_populates="user",
    )

    def __str__(self) -> str:
        return f"{self.username}"
