from fastapi.routing import APIRouter

from live_chat.web.api import chat, monitoring, users

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(users.router)
api_router.include_router(chat.chat_router, prefix="/chats", tags=["chat"])
