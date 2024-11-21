import asyncio
from typing import Any, AsyncGenerator

from live_chat.services.redis import redis


async def message_generator(redis_key: str) -> AsyncGenerator[dict[str, Any], None]:
    """Event generator for sending SSE."""
    try:
        while True:
            if message := await redis.lpop(redis_key):  # type: ignore[misc]
                yield {"event": "new_message", "data": message}
            await asyncio.sleep(0.1)
    except asyncio.CancelledError:
        pass
