# type: ignore
import uuid
from typing import TYPE_CHECKING, List

from fastapi_users_db_sqlalchemy import GUID, UUID_ID
from sqlalchemy import (
    UUID,
    Column,
    Enum,
    ForeignKey,
    String,
    Table,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from live_chat.db.base import Base
from live_chat.db.meta import meta
from live_chat.db.models.enums import ChatType

if TYPE_CHECKING:
    from live_chat.db.models.messages import DraftMessage
    from live_chat.db.models.read_status import ReadStatus
    from live_chat.db.models.summarization import Summarization
    from live_chat.db.models.user import User

chat_participant = Table(
    "chat_participant",
    meta,
    Column("user_id", UUID, ForeignKey("user.id"), primary_key=False),
    Column("chat_id", UUID, ForeignKey("chat.id"), primary_key=False),
)


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
    summarizations: Mapped[List["Summarization"]] = relationship(
        back_populates="chat",
        cascade="all,delete",
    )

    def __str__(self) -> str:
        return f"{self.chat_type.value.title()} {self.id}"
