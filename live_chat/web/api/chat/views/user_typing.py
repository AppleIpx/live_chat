from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from starlette import status
from starlette.responses import JSONResponse

from live_chat.db.models.chat import Chat  # type: ignore[attr-defined]
from live_chat.db.models.user import User
from live_chat.web.api.chat.utils import validate_user_access_to_chat
from live_chat.web.api.messages.utils import publish_faststream
from live_chat.web.api.users.utils import custom_current_user

user_typing_router = APIRouter()


@user_typing_router.post("/{chat_id}/typing-status")
async def send_user_typing(
    is_typing: bool,
    chat: Chat = Depends(validate_user_access_to_chat),
    current_user: User = Depends(custom_current_user),
) -> JSONResponse:
    """Notify that user is typing in chat."""
    event_data = jsonable_encoder(
        {
            "user_id": f"{current_user.id!s}",
            "username": f"{current_user.username!s}",
            "is_typing": is_typing,
        },
    )
    await publish_faststream("user_typing", chat.users, event_data, chat.id)
    return JSONResponse(
        content={"detail": "User typing event send"},
        status_code=status.HTTP_200_OK,
    )
