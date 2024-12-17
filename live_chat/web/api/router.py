from fastapi.routing import APIRouter

from live_chat.web.api import black_list, chat, messages, monitoring, read_status, users

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(users.router)
api_router.include_router(messages.message_router, tags=["chat"])
api_router.include_router(chat.chat_router, prefix="/chats", tags=["chat"])
api_router.include_router(
    read_status.read_status_router,
    prefix="/read_status",
    tags=["read_status"],
)
api_router.include_router(
    black_list.black_list_router,
    prefix="/black-list",
    tags=["black-list"],
)
