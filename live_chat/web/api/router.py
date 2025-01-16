from fastapi.routing import APIRouter

from live_chat.web.api import black_list, chat, messages, monitoring, read_status, users

api_router = APIRouter()

api_router.include_router(monitoring.router)
api_router.include_router(users.router)

# messages
api_router.include_router(messages.deleted_msg_router, tags=["chat"])
api_router.include_router(messages.draft_message_router, tags=["chat"])
api_router.include_router(messages.message_router, tags=["chat"])
api_router.include_router(messages.reaction_router, tags=["chat"])
api_router.include_router(messages.sse_event_router, tags=["chat"])

# chats
api_router.include_router(chat.update_chat_router, prefix="/chats", tags=["chat"])
api_router.include_router(chat.create_chat_router, prefix="/chats", tags=["chat"])
api_router.include_router(chat.get_chat_router, prefix="/chats", tags=["chat"])
api_router.include_router(chat.upload_router, prefix="/chats", tags=["chat"])
api_router.include_router(chat.user_typing_router, prefix="/chats", tags=["chat"])

# read status
api_router.include_router(
    read_status.read_status_router,
    prefix="/read_status",
    tags=["read_status"],
)

# black list
api_router.include_router(
    black_list.black_list_router,
    prefix="/black-list",
    tags=["black-list"],
)
