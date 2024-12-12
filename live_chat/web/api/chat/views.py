from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi_pagination import set_page
from fastapi_pagination.cursor import CursorPage, CursorParams
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status
from starlette.responses import JSONResponse

from live_chat.db.models.chat import (  # type: ignore[attr-defined]
    Chat,
    DeletedMessage,
    ReadStatus,
    User,
)
from live_chat.db.utils import get_async_session
from live_chat.web.api.chat.schemas import (
    ChatSchema,
    CreateDirectChatSchema,
    CreateGroupChatSchema,
    DeletedChatSchema,
    ReadStatusSchema,
    UpdateGroupChatSchema,
)
from live_chat.web.api.chat.utils import (
    create_direct_chat,
    create_group_chat,
    direct_chat_exists,
    transformation_chat,
    validate_user_access_to_chat,
)
from live_chat.web.api.messages.utils import publish_faststream
from live_chat.web.api.read_status.utils import get_read_status_by_user_chat_ids
from live_chat.web.api.users.schemas import UserRead
from live_chat.web.api.users.utils import (
    collect_users_for_group,
    current_active_user,
    get_user_by_id,
    transformation_users,
)
from live_chat.web.utils import ImageSaver

chat_router = APIRouter()


@chat_router.post(
    "/create/direct",
    summary="Create a direct chat",
    response_model=ChatSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_direct_chat_view(
    create_direct_chat_schema: CreateDirectChatSchema,
    db_session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user),
) -> ChatSchema | HTTPException:
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
    read_status: ReadStatus = await get_read_status_by_user_chat_ids(
        db_session=db_session,
        chat_id=chat.id,
        user_id=current_user.id,
    )
    return await transformation_chat(chat, read_status)


@chat_router.post(
    "/create/group",
    summary="Create a group chat",
    response_model=ChatSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_group_chat_view(
    create_group_chat_schema: CreateGroupChatSchema,
    db_session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user),
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
    read_status: ReadStatus = await get_read_status_by_user_chat_ids(
        db_session=db_session,
        chat_id=chat.id,
        user_id=current_user.id,
    )
    return await transformation_chat(chat, read_status)


@chat_router.get("", summary="List chats")
async def get_list_chats_view(
    user_id_exists: UUID | None = None,
    db_session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user),
    params: CursorParams = Depends(),
) -> CursorPage[ChatSchema]:
    """Getting chats to which a user has been added."""
    set_page(CursorPage[ChatSchema])
    query = (
        select(Chat)
        .options(selectinload(Chat.read_status))
        .where(Chat.users.any(id=current_user.id))
        .order_by(Chat.updated_at.desc())
    )
    if user_id_exists and await get_user_by_id(db_session, user_id=user_id_exists):
        query = query.where(Chat.users.any(id=user_id_exists))
    chats = await paginate(db_session, query, params=params)
    read_status_query = (
        select(ReadStatus)
        .where(ReadStatus.user_id == current_user.id)
        .where(ReadStatus.chat_id.in_([chat.id for chat in chats.items]))
    )
    read_statuses = await db_session.execute(read_status_query)
    read_status_dict = {
        status.chat_id: status for status in read_statuses.scalars().all()
    }
    for chat in chats.items:
        chat.read_status = read_status_dict.get(chat.id)
    return chats


@chat_router.get("/deleted", summary="List deleted chats")
async def get_list_deleted_chats_view(
    db_session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user),
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


@chat_router.get(
    "/{chat_id}",
    summary="Detail chat by id",
    response_model=ChatSchema,
)
async def get_detail_chat_view(
    db_session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user),
    chat: Chat = Depends(validate_user_access_to_chat),
) -> ChatSchema:
    """Get detail chat by id."""
    users_data: List[UserRead] = transformation_users(chat.users)
    read_status: ReadStatus = await get_read_status_by_user_chat_ids(
        db_session=db_session,
        chat_id=chat.id,
        user_id=current_user.id,
    )
    read_status_schema = ReadStatusSchema(
        id=read_status.id,
        chat_id=read_status.chat_id,
        user_id=read_status.user_id,
        last_read_message_id=read_status.last_read_message_id,
        count_unread_msg=read_status.count_unread_msg,
    )
    return ChatSchema(
        id=chat.id,
        chat_type=chat.chat_type,
        name=chat.name,
        image=chat.image,
        created_at=chat.created_at,
        updated_at=chat.updated_at,
        users=users_data,
        read_status=read_status_schema,
    )


@chat_router.patch("/{chat_id}/upload-image", summary="Update group image")
async def upload_group_image(
    uploaded_image: UploadFile,
    chat: Chat = Depends(validate_user_access_to_chat),
    db_session: AsyncSession = Depends(get_async_session),
) -> dict[str, str]:
    """Update group image."""

    image_saver = ImageSaver(chat.id)
    image_url = await image_saver.save_image(uploaded_image, "group_images")

    if not image_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image upload",
        )

    if chat.chat_type.value == "direct":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can't specify a photo for direct chat",
        )

    chat.image = image_url
    db_session.add(chat)
    await db_session.commit()
    event_data = jsonable_encoder({"image_url": image_url})
    await publish_faststream("update_image_group", chat.users, event_data, chat.id)
    return {"image_url": image_url}


@chat_router.post("/{chat_id}/typing-status")
async def send_user_typing(
    is_typing: bool,
    chat: Chat = Depends(validate_user_access_to_chat),
    current_user: User = Depends(current_active_user),
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


@chat_router.patch("/{chat_id}", summary="Update chat")
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
