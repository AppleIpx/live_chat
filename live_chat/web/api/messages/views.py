import asyncio
import json
import logging
from typing import Any, AsyncGenerator
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette import EventSourceResponse

from live_chat.db.models.chat import Chat  # type: ignore[attr-defined]
from live_chat.db.utils import get_async_session
from live_chat.services.faststream.router import fast_stream_broker
from live_chat.settings import settings
from live_chat.web.api.chat.utils.check_user_in_chat import validate_user_access_to_chat
from live_chat.web.api.chat.utils.get_chat_by_id import get_chat_by_id
from live_chat.web.api.chat.utils.get_users_chats import get_user_chats
from live_chat.web.api.messages import CreateMessageSchema, GetMessageSchema
from live_chat.web.api.messages.constants import (
    REDIS_CHANNEL_PREFIX,
    REDIS_SSE_KEY_PREFIX,
)
from live_chat.web.api.messages.utils import transformation_message
from live_chat.web.api.messages.utils.get_user_from_token import get_user_from_token
from live_chat.web.api.messages.utils.save_message_to_db import save_message_to_db
from live_chat.web.api.users.schemas import UserManager
from live_chat.web.api.users.utils.utils import get_user_manager

message_router = APIRouter()
logger = logging.getLogger(__name__)
redis = Redis(host=settings.redis_host, port=settings.redis_port, decode_responses=True)


@message_router.post("/chats/{chat_id}/messages/")
async def post_message(
    message: CreateMessageSchema,
    chat: Chat = Depends(validate_user_access_to_chat),
    db_session: AsyncSession = Depends(get_async_session),
) -> dict[str, str] | None:
    """Post message in FastStream."""
    if created_message := await save_message_to_db(db_session, message):
        message_data: GetMessageSchema = transformation_message([created_message])[0]
        for user in chat.users:
            target_channel = f"{REDIS_CHANNEL_PREFIX}:{chat.id!s}:{user.id!s}"
            await fast_stream_broker.publish(
                json.dumps(jsonable_encoder(message_data.model_dump())),
                channel=target_channel,
            )
        return {"status": "Message published"}
    raise HTTPException(
        status_code=404,
        detail="Error with saving message. Please try again",
    )


@fast_stream_broker.subscriber(channel="{REDIS_CHANNEL_PREFIX}:{chat_id}:{user_id}")
async def process_message(message: Any) -> None:
    """Save the message in Redis for SSE subscribers."""
    decoded_message = json.loads(message.body.decode("utf-8"))
    chat_id = message.path["chat_id"]
    user_id = message.path["user_id"]
    redis_key = f"{REDIS_SSE_KEY_PREFIX}{chat_id}_{user_id}"

    await redis.lpush(  # type: ignore[misc]
        redis_key,
        json.dumps(decoded_message, ensure_ascii=False),
    )


async def event_generator(redis_key: str) -> AsyncGenerator[dict[str, Any], None]:
    """Event generator for sending SSE."""
    try:
        while True:
            if message := await redis.lpop(redis_key):  # type: ignore[misc]
                yield {"event": "new_message", "data": message}
            await asyncio.sleep(0.1)
    except asyncio.CancelledError:
        pass


@message_router.get("/chats/{chat_id}/events/")
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
        raise HTTPException(status_code=404, detail="Chat not found")

    user_chats = await get_user_chats(db_session, current_user=current_user)

    if chat not in user_chats:
        raise HTTPException(status_code=403, detail="User is not part of the chat")

    redis_key = f"{REDIS_SSE_KEY_PREFIX}{chat.id}_{current_user.id}"
    return EventSourceResponse(event_generator(redis_key), ping=60)
