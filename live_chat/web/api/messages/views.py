import asyncio
import json
import logging
from typing import Any, AsyncGenerator, Final

from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette import EventSourceResponse

from live_chat.db.models.chat import Chat  # type: ignore[attr-defined]
from live_chat.db.utils import get_async_session
from live_chat.services.faststream.router import fast_stream_broker
from live_chat.settings import settings
from live_chat.web.api.chat.utils.check_user_in_chat import validate_user_access_to_chat
from live_chat.web.api.messages import CreateMessageSchema
from live_chat.web.api.messages.utils.save_message_to_db import save_message_to_db

message_router = APIRouter()
logger = logging.getLogger(__name__)
redis = Redis(host=settings.redis_host, port=settings.redis_port, decode_responses=True)
REDIS_CHANNEL_PREFIX: Final = "chat:"
REDIS_SSE_KEY_PREFIX: Final = "sse:"


@message_router.post("/chats/{chat_id}/messages/")
async def post_message(
    message: CreateMessageSchema,
    chat: Chat = Depends(validate_user_access_to_chat),
    db_session: AsyncSession = Depends(get_async_session),
) -> dict[str, str] | None:
    """Post message in FastStream."""
    if await save_message_to_db(db_session, message):
        await fast_stream_broker.publish(
            json.dumps(jsonable_encoder(message.model_dump())),
            channel=f"{REDIS_CHANNEL_PREFIX}{chat.id}",
        )
        return {"status": "Message published"}
    raise HTTPException(
        status_code=404,
        detail="Error with saving message. Please try again",
    )


@fast_stream_broker.subscriber(f"{REDIS_CHANNEL_PREFIX}{{chat_id}}")
async def process_message(message: Any) -> None:
    """Save the message in Redis for SSE subscribers."""
    decoded_message = json.loads(message.body.decode("utf-8"))
    chat_id = decoded_message["chat"]["id"]
    redis_key = f"{REDIS_SSE_KEY_PREFIX}{chat_id}"
    await redis.rpush(  # type: ignore[misc]
        redis_key,
        json.dumps(decoded_message, ensure_ascii=False),
    )


async def event_generator(redis_key: str) -> AsyncGenerator[dict[str, Any], None]:
    """Event generator for sending SSE."""
    try:
        while True:
            while await redis.llen(redis_key):  # type: ignore[misc]
                message = await redis.lpop(redis_key)  # type: ignore[misc]
                yield {"event": "new_message", "data": message}
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        pass


@message_router.get("/chats/{chat_id}/events/")
async def sse_events(
    chat: Chat = Depends(validate_user_access_to_chat),
) -> EventSourceResponse:
    """Client connection to SSE."""
    redis_key = f"{REDIS_SSE_KEY_PREFIX}{chat.id}"
    return EventSourceResponse(event_generator(redis_key))
