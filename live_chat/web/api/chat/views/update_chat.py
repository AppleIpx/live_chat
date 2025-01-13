from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import JSONResponse

from live_chat.db.models.chat import Chat  # type: ignore[attr-defined]
from live_chat.db.utils import get_async_session
from live_chat.web.api.chat.schemas import UpdateGroupChatSchema
from live_chat.web.api.chat.utils import validate_user_access_to_chat
from live_chat.web.api.messages.utils import publish_faststream

update_chat_router = APIRouter()


@update_chat_router.patch("/{chat_id}", summary="Update chat")
async def update_chat(
    update_schema: UpdateGroupChatSchema,
    chat: Chat = Depends(validate_user_access_to_chat),
    db_session: AsyncSession = Depends(get_async_session),
) -> JSONResponse:
    """Update chat."""
    if chat.chat_type.value == "direct":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can't specify a name chat for direct chat",
        )
    chat.name = update_schema.name_group
    db_session.add(chat)
    await db_session.commit()
    event_data = jsonable_encoder({"group_name": f"{update_schema.name_group}"})
    await publish_faststream("update_group_name", chat.users, event_data, chat.id)
    return JSONResponse("Chat name updated", status_code=status.HTTP_200_OK)
