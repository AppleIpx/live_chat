import json
from typing import Any
from uuid import UUID

from fastapi.encoders import jsonable_encoder

from live_chat.services.faststream import fast_stream_broker
from live_chat.services.redis import redis
from live_chat.web.api.messages.constants import REDIS_SSE_KEY_PREFIX


async def publish_faststream_summarize(
    user_id: UUID,
    chat_id: UUID,
    data: dict[str, Any],
    action: str = "progress_summarization",
) -> None:
    """Publish summarize action in FastStream broker."""
    target_channel = f"Summarize:{chat_id!s}:{user_id!s}"
    event_data = {"event": action, "data": json.dumps(jsonable_encoder(data))}
    await fast_stream_broker.publish(
        json.dumps(event_data),
        channel=target_channel,
    )


@fast_stream_broker.subscriber(channel="Summarize:{chat_id}:{user_id}")
async def process_summarize(message: Any) -> None:
    """Save the message in Redis for SSE subscriber."""
    decoded_message = json.loads(message.body.decode("utf-8"))
    chat_id = message.path["chat_id"]
    user_id = message.path["user_id"]
    event_type = decoded_message.get("event")
    event_data = {"event": event_type, "data": decoded_message["data"]}
    redis_key = f"{REDIS_SSE_KEY_PREFIX}{chat_id}_{user_id}_summarize"

    await redis.lpush(  # type: ignore[misc]
        redis_key,
        json.dumps(event_data, ensure_ascii=False),
    )
