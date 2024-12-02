import json
from typing import Any, List
from uuid import UUID

from live_chat.db.models.chat import User  # type: ignore[attr-defined]
from live_chat.services.faststream import fast_stream_broker
from live_chat.services.redis import redis
from live_chat.web.api.messages.constants import (
    REDIS_CHANNEL_PREFIX,
    REDIS_SSE_KEY_PREFIX,
)


async def publish_faststream(
    action: str,
    users: List[User],
    data: str,
    chat_id: UUID,
) -> None:
    """Publish action in FastStream broker."""
    for user in users:
        target_channel = f"{REDIS_CHANNEL_PREFIX}:{chat_id!s}:{user.id!s}"
        await fast_stream_broker.publish(
            json.dumps({"event": action, "data": json.dumps(data)}),
            channel=target_channel,
        )


@fast_stream_broker.subscriber(channel="{REDIS_CHANNEL_PREFIX}:{chat_id}:{user_id}")
async def process_message(message: Any) -> None:
    """Save the message in Redis for SSE subscribers."""
    decoded_message = json.loads(message.body.decode("utf-8"))
    chat_id = message.path["chat_id"]
    user_id = message.path["user_id"]
    event_type = decoded_message.get("event", "new_message")
    event_data = {"event": event_type, "data": decoded_message["data"]}
    redis_key = f"{REDIS_SSE_KEY_PREFIX}{chat_id}_{user_id}"

    await redis.lpush(  # type: ignore[misc]
        redis_key,
        json.dumps(event_data, ensure_ascii=False),
    )
