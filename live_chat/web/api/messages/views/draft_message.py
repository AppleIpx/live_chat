from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import Response

from live_chat.db.models.chat import Chat, User  # type: ignore[attr-defined]
from live_chat.db.utils import get_async_session
from live_chat.web.api.chat.utils import validate_user_access_to_chat
from live_chat.web.api.messages.schemas import (
    GetDraftMessageSchema,
    PostDraftMessageSchema,
    UpdateMessageSchema,
)
from live_chat.web.api.messages.utils import get_draft_message_by_chat_and_user_ids
from live_chat.web.api.messages.utils.delete_message import delete_message_by_id
from live_chat.web.api.messages.utils.save_message import (
    save_draft_message_to_db,
    update_draft_message_to_db,
)
from live_chat.web.api.messages.utils.transformations import (
    transformation_draft_message,
)
from live_chat.web.api.users.utils import custom_current_user

draft_message_router = APIRouter()


@draft_message_router.post(
    "/chats/{chat_id}/draft-message",
    summary="Create draft message",
    status_code=status.HTTP_201_CREATED,
)
async def post_draft_message_view(
    draft_message_schema: PostDraftMessageSchema,
    current_user: User = Depends(custom_current_user),
    chat: Chat = Depends(validate_user_access_to_chat),
    db_session: AsyncSession = Depends(get_async_session),
) -> GetDraftMessageSchema:
    """Create draft message in chat."""
    draft_message = await save_draft_message_to_db(
        db_session=db_session,
        chat=chat,
        current_user=current_user,
        draft_message_schema=draft_message_schema,
    )
    return await transformation_draft_message(draft_message=draft_message)


@draft_message_router.put(
    "/chats/{chat_id}/draft-message",
    summary="Update draft message",
    status_code=status.HTTP_200_OK,
)
async def update_draft_message_view(
    draft_message_schema: UpdateMessageSchema,
    current_user: User = Depends(custom_current_user),
    chat: Chat = Depends(validate_user_access_to_chat),
    db_session: AsyncSession = Depends(get_async_session),
) -> GetDraftMessageSchema:
    """Update draft message in chat."""
    if draft_message := await get_draft_message_by_chat_and_user_ids(
        db_session=db_session,
        chat_id=chat.id,
        user_id=current_user.id,
    ):
        await update_draft_message_to_db(
            db_session=db_session,
            draft_message=draft_message,
            draft_message_schema=draft_message_schema,
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft message not found",
        )
    await db_session.refresh(draft_message)
    return await transformation_draft_message(draft_message=draft_message)


@draft_message_router.delete(
    "/chats/{chat_id}/draft-message",
    summary="Delete draft message",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_draft_message_view(
    current_user: User = Depends(custom_current_user),
    chat: Chat = Depends(validate_user_access_to_chat),
    db_session: AsyncSession = Depends(get_async_session),
) -> Response:
    """Delete draft message in chat."""
    if draft_message := await get_draft_message_by_chat_and_user_ids(
        db_session=db_session,
        chat_id=chat.id,
        user_id=current_user.id,
    ):
        await delete_message_by_id(
            db_session=db_session,
            message=draft_message,
            chat=chat,
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft message not found",
        )
    await db_session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
