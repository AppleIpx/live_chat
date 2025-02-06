import uuid
from typing import TYPE_CHECKING
from uuid import UUID

from fastapi_users_db_sqlalchemy import GUID
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from live_chat.db.base import Base
from live_chat.db.utils import RemoveBaseFieldsMixin

if TYPE_CHECKING:
    from live_chat.db.models.chat import Chat  # type: ignore[attr-defined]
    from live_chat.db.models.user import User


class ReadStatus(RemoveBaseFieldsMixin, Base):  # type: ignore[misc]
    """Read status model."""

    __tablename__ = "read_status"

    id: Mapped[UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    last_read_message_id: Mapped[UUID] = mapped_column(GUID, nullable=True)
    count_unread_msg: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"))
    chat_id: Mapped[UUID] = mapped_column(ForeignKey("chat.id"))

    chat: Mapped["Chat"] = relationship(back_populates="read_statuses")
    user: Mapped["User"] = relationship(back_populates="read_statuses")

    def __str__(self) -> str:
        return f"User: {self.user_id}, Message: {self.last_read_message_id}"
