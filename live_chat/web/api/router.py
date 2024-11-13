from fastapi.routing import APIRouter

from live_chat.web.api import chat, echo, monitoring, redis, users

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(users.router)
api_router.include_router(echo.router, prefix="/echo", tags=["echo"])
api_router.include_router(redis.router, prefix="/redis", tags=["redis"])
api_router.include_router(chat.chat_router, prefix="/chat", tags=["chat"])
