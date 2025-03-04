from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi_pagination import set_page
from fastapi_pagination.cursor import CursorPage, CursorParams
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status

from live_chat.db.models.chat import Chat  # type: ignore[attr-defined]
from live_chat.db.models.enums import MessageType
from live_chat.db.models.messages import Message
from live_chat.db.models.user import User
from live_chat.db.utils import get_async_session
from live_chat.web.api.black_list.utils import validate_user_in_black_list
from live_chat.web.api.chat.utils import get_chat_by_id, validate_user_access_to_chat
from live_chat.web.api.messages import GetMessageSchema, PostMessageSchema
from live_chat.web.api.messages.schemas import (
    CreatedForwardMessageSchema,
    GetForwardMessageSchema,
    GetParentMessageSchema,
    GetReactionSchema,
    PostForwardMessageSchema,
    UpdateMessageSchema,
)
from live_chat.web.api.messages.utils import (
    check_parent_message,
    get_message_by_id,
    get_messages_range,
    publish_faststream,
    validate_access_to_msg_in_chat,
    validate_message_exists,
    validate_message_schema,
    validate_user_owns_message_access,
)
from live_chat.web.api.messages.utils.save_message import (
    save_forwarded_message,
    save_message_to_db,
)
from live_chat.web.api.messages.utils.transformations import (
    transformation_forward_msg,
    transformation_message,
)
from live_chat.web.api.read_status.utils import increase_in_unread_messages
from live_chat.web.api.users.utils import custom_current_user
from live_chat.web.api.users.utils.transformations import (
    transformation_short_user,
)
from live_chat.web.api.users.utils.validators import validate_user_active

message_router = APIRouter()


@message_router.get("/chats/{chat_id}/messages")
async def get_messages(
    chat: Chat = Depends(validate_user_access_to_chat),
    params: CursorParams = Depends(),
    db_session: AsyncSession = Depends(get_async_session),
) -> CursorPage[GetMessageSchema]:
    """Get messages in chat by pagination."""
    set_page(CursorPage[GetMessageSchema])
    query = (
        select(Message)
        .where(Message.chat_id == chat.id, Message.is_deleted != True)  # noqa: E712
        .options(
            selectinload(Message.reactions),
            selectinload(Message.forwarded_message),
        )
        .order_by(Message.created_at.desc())
    )
    messages = await paginate(db_session, query, params=params)
    for message in messages.items:
        message.reactions = [
            GetReactionSchema(
                id=reaction.id,
                reaction_type=reaction.reaction_type,
                user_id=reaction.user_id,
                message_id=reaction.message_id,
                updated_at=reaction.updated_at,
            )
            for reaction in message.reactions
        ]
        if message.forwarded_message is not None:
            user_schema = transformation_short_user(
                user=message.forwarded_message.user,
            )
            message.forwarded_message = GetForwardMessageSchema(
                id=message.forwarded_message.id,
                user=user_schema,
            )
        else:
            message.forwarded_message = None
        message.parent_message = (
            GetParentMessageSchema(
                id=message.parent_message.id,
                message_type=message.parent_message.message_type,
                file_name=message.parent_message.file_name,
                file_path=message.parent_message.file_path,
                content=message.parent_message.content,
            )
            if message.parent_message
            else None
        )
    return messages


@message_router.get("/chats/{chat_id}/messages/range")
async def get_range_messages(
    from_id: UUID,
    to_id: UUID,
    chat: Chat = Depends(validate_user_access_to_chat),
    db_session: AsyncSession = Depends(get_async_session),
) -> list[GetMessageSchema]:
    """Get a range messages in chat."""
    message_from = await validate_message_exists(
        db_session=db_session,
        message_id=from_id,
    )
    message_to = await validate_message_exists(db_session=db_session, message_id=to_id)
    messages = await get_messages_range(
        db_session=db_session,
        chat_id=chat.id,
        from_date=message_from.created_at,
        to_date=message_to.created_at,
    )
    return [await transformation_message(message) for message in messages]


@message_router.post("/chats/{chat_id}/messages", status_code=status.HTTP_201_CREATED)
async def post_message(
    message_schema: PostMessageSchema,
    chat: Chat = Depends(validate_user_access_to_chat),
    current_user: User = Depends(custom_current_user),
    db_session: AsyncSession = Depends(get_async_session),
    _: None = Depends(validate_message_schema),
) -> GetMessageSchema:
    """Post message in FastStream."""
    if chat.chat_type.value == "direct":
        recipient = chat.users[1]
        await validate_user_active(recipient)
        await validate_user_in_black_list(
            recipient=recipient,
            sender=current_user,
            db_session=db_session,
        )
    await check_parent_message(
        db_session=db_session,
        message_id=message_schema.parent_message_id,
    )
    if created_message := await save_message_to_db(
        db_session=db_session,
        content=message_schema.content,
        parent_message_id=message_schema.parent_message_id,
        chat=chat,
        message_type=message_schema.message_type,
        owner_msg_id=current_user.id,
        file_name=message_schema.file_name,
        file_path=message_schema.file_path,
    ):
        message_data = await transformation_message(created_message)
        event_data = jsonable_encoder(message_data.model_dump())
        await increase_in_unread_messages(
            chat=chat,
            current_user=current_user,
            db_session=db_session,
        )
        await publish_faststream("new_message", chat.users, event_data, chat.id)
        return message_data
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Error with saving message. Please try again",
    )


@message_router.patch(
    "/chats/{chat_id}/messages/{message_id}",
    response_model=GetMessageSchema,
)
async def update_message(
    message_schema: UpdateMessageSchema,
    chat: Chat = Depends(validate_user_access_to_chat),
    message: Message = Depends(validate_user_owns_message_access),
    db_session: AsyncSession = Depends(get_async_session),
) -> GetMessageSchema:
    """Update message."""
    if message_schema.message_type == MessageType.TEXT:
        message.content = message_schema.content
        message.updated_at = datetime.now(timezone.utc)
        chat.last_message_content = message_schema.content[:100]  # type: ignore[index]
        await db_session.commit()
        message_data = await transformation_message(message)
        event_data = jsonable_encoder(message_data.model_dump())
        await publish_faststream("update_message", chat.users, event_data, chat.id)
        return message_data
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="File message cannot updated",
    )


@message_router.post(
    "/chats/{chat_id}/messages/forward",
    response_model=CreatedForwardMessageSchema,
    status_code=status.HTTP_201_CREATED,
)
async def forward_message_view(
    forward_message_schema: PostForwardMessageSchema,
    current_user: User = Depends(custom_current_user),
    chat: Chat = Depends(validate_user_access_to_chat),
    db_session: AsyncSession = Depends(get_async_session),
) -> CreatedForwardMessageSchema:
    """Post forwarding message/messages in other chat."""
    messages = [
        await get_message_by_id(
            db_session=db_session,
            message_id=msg_id,
        )
        for msg_id in forward_message_schema.messages
    ]
    to_chat = await get_chat_by_id(
        db_session=db_session,
        chat_id=forward_message_schema.to_chat_id,
    )
    await validate_access_to_msg_in_chat(
        from_chat=chat,
        to_chat=to_chat,
        current_user=current_user,
        messages=messages,
    )
    forwarded_messages = await save_forwarded_message(
        db_session=db_session,
        orig_messages=messages,
        to_chat=to_chat,
        current_user=current_user,
    )
    list_get_schem = await transformation_forward_msg(
        forward_messages=forwarded_messages,
    )
    data = jsonable_encoder(list_get_schem)
    await publish_faststream("forward_message", to_chat.users, data, to_chat.id)  # type: ignore[union-attr]
    return CreatedForwardMessageSchema(
        forward_messages=list_get_schem,
    )
