import asyncio
import json
from typing import Any, AsyncGenerator

from live_chat.services.redis import redis


async def message_generator(redis_key: str) -> AsyncGenerator[dict[str, Any], None]:
    """Event generator for sending message in SSE."""
    try:
        while True:
            if raw_message := await redis.lpop(redis_key):  # type: ignore[misc]
                message = json.loads(raw_message)
                yield {"event": message["event"], "data": message["data"]}
            await asyncio.sleep(0.1)
    except asyncio.CancelledError:
        pass
