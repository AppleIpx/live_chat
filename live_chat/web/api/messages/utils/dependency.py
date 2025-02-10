from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.enums import MessageType
from live_chat.db.models.messages import DeletedMessage, Message
from live_chat.db.models.user import User
from live_chat.db.utils import get_async_session
from live_chat.web.api.messages.schemas import PostMessageSchema, UpdateMessageSchema
from live_chat.web.api.messages.utils.get_message import (
    get_deleted_message_by_id,
    get_message_by_id,
)
from live_chat.web.api.users.utils import custom_current_user


async def validate_user_owns_message_access(
    message_id: UUID,
    current_user: User = Depends(custom_current_user),
    db_session: AsyncSession = Depends(get_async_session),
) -> Message | DeletedMessage:
    """Validate that the current user has access to his message."""
    message = await get_message_by_id(db_session, message_id=message_id)
    deleted_message = await get_deleted_message_by_id(
        db_session,
        deleted_message_id=message_id,
    )
    if not message and not deleted_message:
        raise HTTPException(status_code=404, detail="Message not found")
    if (message and current_user.id != message.user_id) or (
        deleted_message and current_user.id != deleted_message.user_id
    ):
        raise HTTPException(
            status_code=403,
            detail="User is not the author of this message",
        )

    return message if message else deleted_message  # type: ignore[return-value]


async def validate_message_exists(
    message_id: UUID,
    db_session: AsyncSession = Depends(get_async_session),
) -> Message:
    """Validate that the message exists."""
    if message := await get_message_by_id(db_session, message_id=message_id):
        return message
    raise HTTPException(status_code=404, detail="Message not found")


async def validate_message_schema(
    message_schema: PostMessageSchema | UpdateMessageSchema,
) -> None:
    """Validate message content or file path."""
    if message_schema.message_type == MessageType.TEXT:
        if not message_schema.content:
            raise HTTPException(
                status_code=400,
                detail="Content is required for text messages.",
            )
    elif not message_schema.file_path or not message_schema.file_name:
        raise HTTPException(
            status_code=400,
            detail="File path and name is required for file messages.",
        )
