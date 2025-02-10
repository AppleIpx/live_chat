from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from live_chat.db.base import Base


class BlockedUsers(Base):
    """Association table for the MTM relationship between Blacklist and User."""

    __tablename__ = "blocked_users"

    blacklist_id: Mapped[UUID] = mapped_column(
        ForeignKey("blacklist.id"),
        primary_key=True,
    )
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"), primary_key=True)
