import logging
from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.chat import Chat, Message, User  # type: ignore[attr-defined]
from live_chat.web.api.chat.schemas import CreateMessageSchema
from live_chat.web.websocket.enums import WebSocketMessageActions


class ActionTypeMixin(BaseModel):
    """Adds a field to the schemas for the websocket."""

    action_type: WebSocketMessageActions


class UsageModelMixin:
    """Implements methods for models usage."""

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

    @staticmethod
    async def save_message_to_db(
        db_session: AsyncSession,
        message_data: CreateMessageSchema,
    ) -> Message | None:
        """Save the message to the database."""
        chat = await db_session.get(Chat, message_data.chat.id)
        user = await db_session.get(User, message_data.user.id)

        if not chat or not user:
            logging.error("Data error. Chat or user not found.", exc_info=True)
            return None

        message = Message(
            content=message_data.content,
            chat_id=chat.id,
            user_id=user.id,
        )
        chat.updated_at = datetime.now()

        db_session.add(message)
        await db_session.commit()
        await db_session.refresh(message)

        return message
