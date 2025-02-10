# type: ignore
import uuid
from datetime import datetime
from typing import List

from fastapi_users_db_sqlalchemy import GUID, UUID_ID, SQLAlchemyBaseUserTableUUID
from sqlalchemy import (
    JSON,
    UUID,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Table,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from live_chat.db.base import Base
from live_chat.db.meta import meta
from live_chat.db.models.enums import ChatType, MessageType, TaskStatus, TaskType
from live_chat.db.utils import RemoveBaseFieldsMixin

chat_participant = Table(
    "chat_participant",
    meta,
    Column("user_id", UUID, ForeignKey("user.id"), primary_key=False),
    Column("chat_id", UUID, ForeignKey("chat.id"), primary_key=False),
)


class BaseMessage(Base):
    """Abstract base class for messages."""

    __abstract__ = True

    id: Mapped[UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    message_type: Mapped[str] = mapped_column(
        Enum(MessageType, inherit_schema=True),
        default=MessageType.TEXT,
    )
    content: Mapped[str] = mapped_column(String(5000), nullable=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"))
    chat_id: Mapped[UUID] = mapped_column(ForeignKey("chat.id"))
    file_name: Mapped[str] = mapped_column(String(50), nullable=True)
    file_path: Mapped[str] = mapped_column(String(1000), nullable=True)
    parent_message_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("message.id"),
        nullable=True,
    )


class BaseWarning(Base):
    """Abstract base class for warnings."""

    __abstract__ = True

    id: Mapped[UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    reason = Column(String(500), nullable=False)
    ai_detection = Column(Boolean, default=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"))
    correction_deadline = mapped_column(DateTime(timezone=True), nullable=True)


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
    parent_message: Mapped["Message"] = relationship(
        "Message",
        remote_side="Message.id",
        backref="replies",
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


class WarningFirstName(BaseWarning):
    """Warning name."""

    __tablename__ = "warning_firstname"

    user = relationship("User", backref="warning_firstname")

    def __str__(self) -> str:
        return f"Warning first name: {self.user.first_name}"


class WarningLastName(BaseWarning):
    """Warning last name."""

    __tablename__ = "warning_lastname"

    user = relationship("User", backref="warning_lastname")

    def __str__(self) -> str:
        return f"Warning last name: {self.user.last_name}"


class WarningUsername(BaseWarning):
    """Warning username."""

    __tablename__ = "warning_username"

    user = relationship("User", backref="warning_username")

    def __str__(self) -> str:
        return f"Warning username: {self.user.username}"


class Chat(Base):
    """Chat model."""

    __tablename__ = "chat"

    id: Mapped[UUID_ID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    chat_type: Mapped[ChatType] = mapped_column(Enum(ChatType, inherit_schema=True))
    name: Mapped[str] = mapped_column(String(50), nullable=True, default=None)
    image: Mapped[str] = mapped_column(String(1048), nullable=True, default=None)
    last_message_content: Mapped[str] = mapped_column(
        String(100),
        nullable=True,
        default=None,
    )
    draft_messages: Mapped[List["DraftMessage"]] = relationship(
        back_populates="chat",
        cascade="all,delete",
    )

    users: Mapped[List["User"]] = relationship(
        secondary="chat_participant",
        back_populates="chats",
    )
    messages = relationship(
        "Message",
        back_populates="chat",
        overlaps="deleted_messages",
    )
    deleted_messages = relationship(
        "DeletedMessage",
        back_populates="chat",
        overlaps="messages",
    )
    read_statuses: Mapped[List["ReadStatus"]] = relationship(
        back_populates="chat",
        cascade="all,delete",
    )
    tasks: Mapped[List["Task"]] = relationship(
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
    count_unread_msg: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"))
    chat_id: Mapped[UUID] = mapped_column(ForeignKey("chat.id"))

    chat: Mapped[Chat] = relationship(back_populates="read_statuses")
    user: Mapped["User"] = relationship(back_populates="read_statuses")

    def __str__(self) -> str:
        return f"User: {self.user_id}, Message: {self.last_read_message_id}"


class Reaction(Base):
    """Represents a reaction to a message."""

    __tablename__ = "reaction"

    id: Mapped[UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    reaction_type: Mapped[str] = mapped_column(String(50), nullable=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"), nullable=False)
    message_id: Mapped[UUID] = mapped_column(ForeignKey("message.id"), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="reactions")
    message: Mapped["Message"] = relationship("Message", back_populates="reactions")

    __table_args__ = (
        UniqueConstraint("user_id", "message_id", name="unique_reaction_per_message"),
    )

    def __str__(self) -> str:
        return f"Reaction {self.reaction_type} by {self.user_id} on {self.message_id}"


class BlackList(Base):
    """Represents a blacklist for a user."""

    __tablename__ = "blacklist"

    id: Mapped[UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"))

    blocked_users: Mapped[List["User"]] = relationship(
        "User",
        secondary="blocked_users",
        back_populates="black_list",
    )
    owner = relationship("User", back_populates="black_list")


class BlockedUsers(Base):
    """Association table for the MTM relationship between Blacklist and User."""

    __tablename__ = "blocked_users"

    blacklist_id: Mapped[UUID] = mapped_column(
        ForeignKey("blacklist.id"),
        primary_key=True,
    )
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"), primary_key=True)


class User(SQLAlchemyBaseUserTableUUID, Base):
    """Represents a user entity."""

    __tablename__ = "user"

    username: Mapped[str] = mapped_column(String(150), unique=True)
    first_name: Mapped[str] = mapped_column(String(150), default="")
    last_name: Mapped[str] = mapped_column(String(150), default="")
    last_online: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    user_image: Mapped[str] = mapped_column(String(1048), nullable=True)

    chats: Mapped[List["Chat"]] = relationship(
        secondary="chat_participant",
        back_populates="users",
    )
    messages = relationship(
        "Message",
        back_populates="user",
        overlaps="deleted_messages",
    )
    deleted_messages = relationship(
        "DeletedMessage",
        back_populates="user",
        overlaps="messages",
    )
    read_statuses: Mapped[List["ReadStatus"]] = relationship(
        back_populates="user",
    )
    reactions: Mapped[List["Reaction"]] = relationship(
        "Reaction",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    black_list: Mapped["BlackList"] = relationship(back_populates="owner")
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    ban_reason: Mapped[str] = mapped_column(String(1048), nullable=True)
    draft_messages: Mapped[List["DraftMessage"]] = relationship(
        back_populates="user",
        cascade="all,delete",
    )
    is_warning: Mapped[bool] = mapped_column(Boolean, default=False)
    tasks: Mapped[List["Task"]] = relationship(
        back_populates="user",
        cascade="all,delete",
    )

    def __str__(self) -> str:
        return f"{self.username}"


class Task(Base):  # type: ignore[misc]
    """Background tasks model."""

    __tablename__ = "task"

    id: Mapped[UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    type: Mapped[TaskType] = mapped_column(Enum(TaskType, inherit_schema=True))
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus, inherit_schema=True),
    )
    result: Mapped[dict] = mapped_column(JSON, default={})
    finished_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"))
    chat_id: Mapped[UUID] = mapped_column(ForeignKey("chat.id"))

    chat: Mapped[Chat] = relationship(back_populates="tasks")
    user: Mapped["User"] = relationship(back_populates="tasks")

    def __str__(self) -> str:
        return f"Task {self.id} - {self.type} - {self.status}"
