import uuid
from datetime import datetime
from uuid import UUID

from fastapi_users_db_sqlalchemy import GUID
from sqlalchemy import JSON, DateTime, Enum, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from live_chat.db.base import Base
from live_chat.db.models.chat import Chat, User  # type: ignore[attr-defined]
from live_chat.db.models.enums import SummarizationStatus


class Summarization(Base):  # type: ignore[misc]
    """Summarizations model."""

    __tablename__ = "summarization"

    id: Mapped[UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    status: Mapped[SummarizationStatus] = mapped_column(
        Enum(SummarizationStatus, inherit_schema=True),
    )
    progres: Mapped[float] = mapped_column(Float, defalt=0.0)
    result: Mapped[JSON] = mapped_column(JSON, default={})
    finished_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"))
    chat_id: Mapped[UUID] = mapped_column(ForeignKey("chat.id"))

    chat: Mapped["Chat"] = relationship(back_populates="summarizations")
    user: Mapped["User"] = relationship(back_populates="summarizations")

    def __str__(self) -> str:
        return f"Summarization {self.id} - {self.status}"
