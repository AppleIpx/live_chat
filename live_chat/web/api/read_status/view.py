from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from live_chat.db.models.chat import (  # type: ignore[attr-defined]
    Chat,
    User,
)
from live_chat.db.utils import get_async_session
from live_chat.web.api.chat.schemas import ReadStatusSchema, UpdateReadStatusSchema
from live_chat.web.api.chat.utils import validate_user_access_to_chat
from live_chat.web.api.read_status.utils import get_read_status_by_user_chat_ids
from live_chat.web.api.users.utils import current_active_user

read_status_router = APIRouter()


@read_status_router.patch(
    "/{chat_id}/update",
    summary="Update read status",
    response_model=ReadStatusSchema,
    status_code=status.HTTP_200_OK,
)
async def update_read_status(
    update_read_status: UpdateReadStatusSchema,
    chat: Chat = Depends(validate_user_access_to_chat),
    db_session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user),
) -> ReadStatusSchema | HTTPException:
    """Update read status."""
    if read_status := await get_read_status_by_user_chat_ids(
        db_session=db_session,
        user_id=current_user.id,
        chat_id=chat.id,
    ):
        read_status.last_read_message_id = update_read_status.last_read_message_id
        db_session.add(read_status)
        await db_session.commit()
        await db_session.refresh(read_status)
        return ReadStatusSchema(
            id=read_status.id,
            last_read_message_id=read_status.last_read_message_id,
            user_id=read_status.user_id,
            chat_id=read_status.chat_id,
            count_unread_msg=update_read_status.count_unread_msg,
        )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Read status not found for the given chat and user.",
    )
