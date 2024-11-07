from faststream.redis.fastapi import RedisRouter

from live_chat.settings import settings

fast_stream_router = RedisRouter(f"{settings.redis_url}")
