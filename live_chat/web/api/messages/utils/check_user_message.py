from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.chat import Message, User  # type: ignore[attr-defined]
from live_chat.db.utils import get_async_session
from live_chat.web.api.chat.utils.get_message_by_id import get_message_by_id
from live_chat.web.api.users.utils import current_active_user


async def validate_user_access_to_message(
    message_id: UUID,
    current_user: User = Depends(current_active_user),
    db_session: AsyncSession = Depends(get_async_session),
) -> Message:
    """Validate that the current user has access to the message."""
    message = await get_message_by_id(db_session, message_id=message_id)

    if message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    if current_user.id != message.user_id:
        raise HTTPException(
            status_code=403,
            detail="User is not the author of this message",
        )

    return message
