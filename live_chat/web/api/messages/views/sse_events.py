from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette import EventSourceResponse
from starlette import status

from live_chat.db.utils import get_async_session
from live_chat.web.api.chat.utils import get_chat_by_id, get_user_chats
from live_chat.web.api.messages.constants import REDIS_SSE_KEY_PREFIX
from live_chat.web.api.messages.utils import get_user_from_token, message_generator
from live_chat.web.api.users.user_manager import UserManager
from live_chat.web.api.users.utils import get_user_manager

sse_event_router = APIRouter()


@sse_event_router.get("/chats/{chat_id}/events")
async def sse_events(
    chat_id: UUID,
    token: str = Query(..., alias="token"),
    db_session: AsyncSession = Depends(get_async_session),
    user_manager: UserManager = Depends(get_user_manager),
) -> EventSourceResponse:
    """Client connection to SSE."""
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

    redis_key = f"{REDIS_SSE_KEY_PREFIX}{chat.id}_{current_user.id}"
    return EventSourceResponse(message_generator(redis_key), ping=60)
