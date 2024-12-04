from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi_pagination import set_page
from fastapi_pagination.cursor import CursorPage, CursorParams
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from live_chat.db.models.chat import (  # type: ignore[attr-defined]
    Chat,
    DeletedMessage,
    User,
)
from live_chat.db.utils import get_async_session
from live_chat.web.api.chat.schemas import (
    ChatSchema,
    CreateDirectChatSchema,
    CreateGroupChatSchema,
)
from live_chat.web.api.chat.utils import (
    create_direct_chat,
    create_group_chat,
    direct_chat_exists,
    transformation_chat,
    validate_user_access_to_chat,
)
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
    return await transformation_chat(chat)


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
    return await transformation_chat(chat)


@chat_router.get("", summary="List chats")
async def get_list_chats_view(
    db_session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user),
    params: CursorParams = Depends(),
) -> CursorPage[ChatSchema]:
    """Getting chats to which a user has been added."""
    set_page(CursorPage[ChatSchema])
    query = (
        select(Chat)
        .where(Chat.users.any(id=current_user.id))
        .order_by(Chat.updated_at.desc())
    )
    return await paginate(db_session, query, params=params)


@chat_router.get("/deleted", summary="List deleted chats")
async def get_list_deleted_chats_view(
    db_session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user),
    params: CursorParams = Depends(),
) -> CursorPage[ChatSchema]:
    """Getting deleted chats to which a user has been added."""
    set_page(CursorPage[ChatSchema])
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
    chat: Chat = Depends(validate_user_access_to_chat),
) -> ChatSchema:
    """Get detail chat by id."""
    users_data: List[UserRead] = transformation_users(chat.users)
    return ChatSchema(
        id=chat.id,
        chat_type=chat.chat_type,
        name=chat.name,
        image=chat.image,
        created_at=chat.created_at,
        updated_at=chat.updated_at,
        users=users_data,
    )


@chat_router.patch("/{chat_id}/upload-image", summary="Update group image")
async def upload_group_image(
    chat_id: UUID,
    uploaded_image: UploadFile,
    user: User = Depends(current_active_user),
    db_session: AsyncSession = Depends(get_async_session),
) -> dict[str, str]:
    """Update group image."""

    image_saver = ImageSaver(chat_id)
    image_url = await image_saver.save_image(uploaded_image, "group_images")

    if not image_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image upload",
        )

    chat = await db_session.get(Chat, chat_id)
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found",
        )
    if chat.chat_type.value == "direct":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can't specify a photo for direct chat",
        )

    chat.image = image_url
    db_session.add(chat)
    await db_session.commit()

    return {"image_url": image_url}
