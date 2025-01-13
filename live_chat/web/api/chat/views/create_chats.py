from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from live_chat.db.models.chat import (  # type: ignore[attr-defined]
    Chat,
    ReadStatus,
    User,
)
from live_chat.db.utils import get_async_session
from live_chat.web.api.chat import ChatSchema, CreateDirectChatSchema
from live_chat.web.api.chat.schemas import CreateGroupChatSchema
from live_chat.web.api.chat.utils import (
    create_direct_chat,
    create_group_chat,
    direct_chat_exists,
    transformation_chat,
)
from live_chat.web.api.read_status.utils.get_read_status_by_id import (
    get_read_statuses_by_chat_id,
)
from live_chat.web.api.users.utils import (
    collect_users_for_group,
    custom_current_user,
    get_user_by_id,
)

create_chat_router = APIRouter()


@create_chat_router.post(
    "/create/direct",
    summary="Create a direct chat",
    response_model=ChatSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_direct_chat_view(
    create_direct_chat_schema: CreateDirectChatSchema,
    db_session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(custom_current_user),
) -> ChatSchema:
    """Create a new direct chat between the current user and a recipient user.

    This endpoint allows the current user to initiate a direct chat with another user.
    It verifies that the recipient user exists and
    that there is no existing chat between
    the two users before creating a new chat.

    Returns:
        ChatSchema: The newly created chat information,
        serialized according to the response model.
    """
    # check if another user (recipient) exists
    recipient_user_id = create_direct_chat_schema.recipient_user_id
    recipient_user: User | None = await get_user_by_id(
        db_session,
        user_id=recipient_user_id,
    )
    # must check that recipient user is not the same as initiator
    if not recipient_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"There is no recipient user with id [{recipient_user_id}]",
        )
    if recipient_user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This user has been deleted.",
        )

    if await direct_chat_exists(
        db_session,
        current_user=current_user,
        recipient_user=recipient_user,
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Chat with recipient user exists [{recipient_user_id}]",
        )

    chat: Chat = await create_direct_chat(
        db_session=db_session,
        initiator_user=current_user,
        recipient_user=recipient_user,
    )
    read_statuses: List[ReadStatus] = await get_read_statuses_by_chat_id(
        db_session=db_session,
        chat_id=chat.id,
    )
    return await transformation_chat(
        chat=chat,
        read_statuses=read_statuses,
        draft_message=None,
    )


@create_chat_router.post(
    "/create/group",
    summary="Create a group chat",
    response_model=ChatSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_group_chat_view(
    create_group_chat_schema: CreateGroupChatSchema,
    db_session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(custom_current_user),
) -> ChatSchema:
    """Create a new group chat."""
    # check if another user (recipient) exists
    recipient_users_id: List[UUID] = create_group_chat_schema.recipient_user_ids
    recipient_users: List[User] = await collect_users_for_group(
        recipient_users_id=recipient_users_id,
        db_session=db_session,
    )
    chat: Chat = await create_group_chat(
        db_session=db_session,
        initiator_user=current_user,
        recipient_users=recipient_users,
        create_group_chat_schema=create_group_chat_schema,
    )
    read_statuses: List[ReadStatus] = await get_read_statuses_by_chat_id(
        db_session=db_session,
        chat_id=chat.id,
    )
    return await transformation_chat(
        chat=chat,
        read_statuses=read_statuses,
        draft_message=None,
    )
