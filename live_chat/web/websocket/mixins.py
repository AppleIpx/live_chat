from pydantic import BaseModel
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.chat import User  # type: ignore[attr-defined]
from live_chat.web.websocket.enums import WebSocketActionType


class ActionTypeMixin(BaseModel):
    """Adds a field to the schemas for the websocket."""

    action_type: WebSocketActionType


class SelectUserMixin:
    """Implements methods for user capture."""

    @staticmethod
    async def get_user_by_username(
        db_session: AsyncSession,
        *,
        username: str,
    ) -> User | None:
        """Getting a user by username."""

        query = select(User).where(or_(User.username == username))
        result = await db_session.execute(query)
        return result.scalar_one_or_none()
