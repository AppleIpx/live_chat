from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from live_chat.db.base import Base

if TYPE_CHECKING:
    from live_chat.db.models.black_list import BlackList
    from live_chat.db.models.chat import Chat  # type: ignore[attr-defined]
    from live_chat.db.models.messages import DraftMessage
    from live_chat.db.models.reaction import Reaction
    from live_chat.db.models.read_status import ReadStatus
    from live_chat.db.models.summarization import Summarization


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
    ban_reason: Mapped[Optional[str]] = mapped_column(String(1048), nullable=True)
    draft_messages: Mapped[List["DraftMessage"]] = relationship(
        back_populates="user",
        cascade="all,delete",
    )
    is_warning: Mapped[bool] = mapped_column(Boolean, default=False)
    summarizations: Mapped[List["Summarization"]] = relationship(
        back_populates="user",
        cascade="all,delete",
    )

    def __str__(self) -> str:
        return f"{self.username}"
