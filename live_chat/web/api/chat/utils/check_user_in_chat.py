from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.chat import Chat, User  # type: ignore[attr-defined]
from live_chat.db.utils import get_async_session
from live_chat.web.api.chat.utils.get_chat import get_chat_by_id
from live_chat.web.api.chat.utils.get_users_chats import get_user_chats
from live_chat.web.api.users.utils import custom_current_user


async def validate_user_access_to_chat(
    chat_id: UUID,
    current_user: User = Depends(custom_current_user),
    db_session: AsyncSession = Depends(get_async_session),
) -> Chat:
    """Validate that the current user has access to the chat."""
    chat = await get_chat_by_id(db_session=db_session, chat_id=chat_id)

    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    user_chats = await get_user_chats(db_session=db_session, current_user=current_user)
    if chat not in user_chats:
        raise HTTPException(status_code=403, detail="User is not part of the chat")

    return chat
