from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from live_chat.db.models.chat import Chat, User  # type: ignore[attr-defined]
from live_chat.db.utils import get_async_session
from live_chat.web.api.chat import (
    ChatDirectSchema,
    CreateChatDirectSchema,
    GetListChatsSchema,
)
from live_chat.web.api.chat.schemas import (
    ChatGroupSchema,
    ChatsSchema,
    CreateGroupChatSchema,
)
from live_chat.web.api.chat.utils.check_direct_chat_exists import direct_chat_exists
from live_chat.web.api.chat.utils.create_chats import (
    create_direct_chat,
    create_group_chat,
)
from live_chat.web.api.chat.utils.get_chat_by_id import get_chat_by_id
from live_chat.web.api.chat.utils.get_users_chats import (
    get_user_chats,
)
from live_chat.web.api.chat.utils.transformations import (
    transformation_chat_direct,
    transformation_chat_group,
    transformation_list_chats,
)
from live_chat.web.api.messages import GetListMessagesDirectSchema, GetMessageSchema
from live_chat.web.api.messages.utils import transformation_message
from live_chat.web.api.users.schemas import UserRead
from live_chat.web.api.users.utils.collect_users_for_group import (
    collect_users_for_group,
)
from live_chat.web.api.users.utils.get_list_users import transformation_users
from live_chat.web.api.users.utils.get_user_by_id import get_user_by_id
from live_chat.web.api.users.utils.utils import current_active_user

chat_router = APIRouter()


@chat_router.post(
    "/create/direct/",
    summary="Create a direct chat",
    response_model=ChatDirectSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_direct_chat_view(
    create_direct_chat_schema: CreateChatDirectSchema,
    db_session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user),
) -> ChatDirectSchema | HTTPException:
    """Create a new direct chat between the current user and a recipient user.

    This endpoint allows the current user to initiate a direct chat with another user.
    It verifies that the recipient user exists and
    that there is no existing chat between
    the two users before creating a new chat.

    Returns:
        ChatDirectSchema: The newly created chat information,
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
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"There is no recipient user with id [{recipient_user_id}]",
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
    return await transformation_chat_direct(chat)


@chat_router.post(
    "/create/group/",
    summary="Create a group chat",
    response_model=ChatGroupSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_group_chat_view(
    create_group_chat_schema: CreateGroupChatSchema,
    db_session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user),
) -> ChatGroupSchema | HTTPException:
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
    return await transformation_chat_group(chat)


@chat_router.get(
    "/",
    summary="List chats",
    response_model=GetListChatsSchema,
)
async def get_list_chats_view(
    db_session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user),
) -> GetListChatsSchema:
    """Getting chats to which a user has been added."""
    chats: List[Chat] = await get_user_chats(db_session, current_user=current_user)
    chats_data: ChatsSchema = transformation_list_chats(chats)

    return GetListChatsSchema(chats=chats_data)


@chat_router.get(
    "/{chat_id}/",
    summary="Detail chat by id",
    response_model=GetListMessagesDirectSchema,
)
async def get_detail_chat_view(
    chat_id: UUID,
    db_session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user),
) -> GetListMessagesDirectSchema:
    """Get detail chat by id."""
    chat: Chat | None = await get_chat_by_id(db_session, chat_id=chat_id)
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat with provided guid does not exist",
        )
    user: User | None = await get_user_by_id(db_session, user_id=current_user.id)
    if user not in chat.users:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You don't have access to this chat",
        )
    users_data: List[UserRead] = transformation_users(chat.users)
    messages_data: List[GetMessageSchema] = transformation_message(chat.messages)

    return GetListMessagesDirectSchema(
        id=chat.id,
        chat_type=chat.chat_type,
        created_at=chat.created_at,
        updated_at=chat.updated_at,
        users=users_data,
        messages=messages_data,
    )
