from uuid import UUID

from fastapi import APIRouter, Depends
from sse_starlette import EventSourceResponse

from live_chat.db.models.chat import User  # type: ignore[attr-defined]
from live_chat.web.api.messages.constants import REDIS_SSE_KEY_PREFIX
from live_chat.web.api.messages.utils import message_generator
from live_chat.web.utils.validate_sse_events import validate_user_in_chat_sse

sse_event_router = APIRouter()


@sse_event_router.get("/chats/{chat_id}/events")
async def sse_events(
    chat_id: UUID,
    user: User = Depends(validate_user_in_chat_sse),
) -> EventSourceResponse:
    """Client connection to SSE."""
    redis_key = f"{REDIS_SSE_KEY_PREFIX}{chat_id}_{user.id}"
    return EventSourceResponse(message_generator(redis_key), ping=60)
