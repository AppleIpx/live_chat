from uuid import UUID

from fastapi import Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from live_chat.db.models.user import User
from live_chat.db.utils import get_async_session
from live_chat.web.api.chat.utils import get_chat_by_id, get_user_chats
from live_chat.web.api.messages.utils import get_user_from_token
from live_chat.web.api.users.user_manager import UserManager
from live_chat.web.api.users.utils import get_user_manager


async def validate_user_in_chat_sse(
    chat_id: UUID,
    token: str = Query(..., alias="token"),
    db_session: AsyncSession = Depends(get_async_session),
    user_manager: UserManager = Depends(get_user_manager),
) -> User:
    """Check user is part of chat in sse events."""
    current_user = await get_user_from_token(token, user_manager)
    chat = await get_chat_by_id(db_session, chat_id=chat_id)

    if chat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found",
        )

    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    user_chats = await get_user_chats(db_session, current_user=current_user)

    if chat not in user_chats:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not part of the chat",
        )
    return current_user
