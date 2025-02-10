import uuid
from typing import TYPE_CHECKING, List
from uuid import UUID

from fastapi_users_db_sqlalchemy import GUID
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from live_chat.db.base import Base

if TYPE_CHECKING:
    from live_chat.db.models.user import User


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
