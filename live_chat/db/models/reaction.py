import uuid
from typing import TYPE_CHECKING
from uuid import UUID

from fastapi_users_db_sqlalchemy import GUID
from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from live_chat.db.base import Base
from live_chat.db.models.messages import Message

if TYPE_CHECKING:
    from live_chat.db.models.user import User


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
