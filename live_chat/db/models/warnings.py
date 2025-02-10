import uuid
from typing import TYPE_CHECKING
from uuid import UUID

from fastapi_users_db_sqlalchemy import GUID
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from live_chat.db.base import Base

if TYPE_CHECKING:
    from live_chat.db.models.user import User


class BaseWarning(Base):
    """Abstract base class for warnings."""

    __abstract__ = True

    id: Mapped[UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    reason = Column(String(500), nullable=False)
    ai_detection = Column(Boolean, default=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"))
    correction_deadline = mapped_column(DateTime(timezone=True), nullable=True)


class WarningFirstName(BaseWarning):
    """Warning name."""

    __tablename__ = "warning_firstname"

    user: Mapped["User"] = relationship("User", backref="warning_firstname")

    def __str__(self) -> str:
        return f"Warning first name: {self.user.first_name}"


class WarningLastName(BaseWarning):
    """Warning last name."""

    __tablename__ = "warning_lastname"

    user: Mapped["User"] = relationship("User", backref="warning_lastname")

    def __str__(self) -> str:
        return f"Warning last name: {self.user.last_name}"


class WarningUsername(BaseWarning):
    """Warning username."""

    __tablename__ = "warning_username"

    user: Mapped["User"] = relationship("User", backref="warning_username")

    def __str__(self) -> str:
        return f"Warning username: {self.user.username}"
