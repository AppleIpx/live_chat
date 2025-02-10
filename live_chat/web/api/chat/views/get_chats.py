from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi_pagination import set_page
from fastapi_pagination.cursor import CursorPage, CursorParams
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from live_chat.db.models.chat import Chat  # type: ignore[attr-defined]
from live_chat.db.models.messages import DeletedMessage
from live_chat.db.models.read_status import ReadStatus
from live_chat.db.models.user import User
from live_chat.db.utils import get_async_session
from live_chat.web.api.chat import ChatSchema
from live_chat.web.api.chat.schemas import DeletedChatSchema, ReadStatusSchema
from live_chat.web.api.chat.utils import (
    get_draft_messages,
    get_read_statuses,
    validate_user_access_to_chat,
)
from live_chat.web.api.messages.utils import get_draft_message_by_chat_and_user_ids
from live_chat.web.api.read_status.utils.get_read_status_by_id import (
    get_read_statuses_by_chat_id,
)
from live_chat.web.api.users.schemas import UserShortRead
from live_chat.web.api.users.utils import custom_current_user, get_user_by_id
from live_chat.web.api.users.utils.transformations import transformation_short_users

get_chat_router = APIRouter()


@get_chat_router.get("", summary="List chats")
async def get_list_chats_view(
    user_id_exists: UUID | None = None,
    db_session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(custom_current_user),
    params: CursorParams = Depends(),
) -> CursorPage[ChatSchema]:
    """Getting chats to which a user has been added."""
    set_page(CursorPage[ChatSchema])
    query = (
        select(Chat)
        .options(selectinload(Chat.read_statuses))
        .options(selectinload(Chat.draft_messages))
        .where(Chat.users.any(id=current_user.id))
        .order_by(Chat.updated_at.desc())
    )
    if user_id_exists and await get_user_by_id(db_session, user_id=user_id_exists):
        query = query.where(Chat.users.any(id=user_id_exists))
    chats = await paginate(db_session, query, params=params)
    read_status_dict = await get_read_statuses(
        db_session=db_session,
        current_user=current_user,
        chats=chats,
    )
    draft_messages_dict = await get_draft_messages(
        db_session=db_session,
        current_user=current_user,
        chats=chats,
    )
    for chat in chats.items:
        chat.read_statuses = [read_status_dict.get(chat.id)]
        chat.draft_message = draft_messages_dict.get(chat.id)
    return chats


@get_chat_router.get("/deleted", summary="List deleted chats")
async def get_list_deleted_chats_view(
    db_session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(custom_current_user),
    params: CursorParams = Depends(),
) -> CursorPage[DeletedChatSchema]:
    """Getting deleted chats to which a user has been added."""
    set_page(CursorPage[DeletedChatSchema])
    subquery = (
        select(func.max(DeletedMessage.created_at).label("last_deleted_at"))
        .where(DeletedMessage.chat_id == Chat.id)
        .correlate(Chat)
        .scalar_subquery()
    )
    query = (
        select(Chat)
        .where(Chat.deleted_messages.any(user_id=current_user.id))
        .order_by(subquery.desc())
    )
    return await paginate(db_session, query, params=params)


@get_chat_router.get(
    "/{chat_id}",
    summary="Detail chat by id",
    response_model=ChatSchema,
)
async def get_detail_chat_view(
    db_session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(custom_current_user),
    chat: Chat = Depends(validate_user_access_to_chat),
) -> ChatSchema:
    """Get detail chat by id."""
    users_data: List[UserShortRead] = transformation_short_users(chat.users)
    read_statuses: List[ReadStatus] = await get_read_statuses_by_chat_id(
        db_session=db_session,
        chat_id=chat.id,
    )
    draft_message = await get_draft_message_by_chat_and_user_ids(
        db_session=db_session,
        chat_id=chat.id,
        user_id=current_user.id,
    )
    read_statuses_schema = [
        ReadStatusSchema(
            id=read_status.id,
            chat_id=read_status.chat_id,
            user_id=read_status.user_id,
            last_read_message_id=read_status.last_read_message_id,
            count_unread_msg=read_status.count_unread_msg,
        )
        for read_status in read_statuses
    ]
    return ChatSchema(
        id=chat.id,
        chat_type=chat.chat_type,
        name=chat.name,
        image=chat.image,
        created_at=chat.created_at,
        updated_at=chat.updated_at,
        users=users_data,
        read_statuses=read_statuses_schema,
        last_message_content=chat.last_message_content,
        draft_message=draft_message.content if draft_message else None,
    )
