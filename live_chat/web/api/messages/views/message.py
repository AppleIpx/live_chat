from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi_pagination import set_page
from fastapi_pagination.cursor import CursorPage, CursorParams
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from live_chat.db.models.chat import Chat, Message, User  # type: ignore[attr-defined]
from live_chat.db.models.enums import MessageType
from live_chat.db.utils import get_async_session
from live_chat.web.api.black_list.utils import validate_user_in_black_list
from live_chat.web.api.chat.utils import validate_user_access_to_chat
from live_chat.web.api.messages import GetMessageSchema, PostMessageSchema
from live_chat.web.api.messages.schemas import GetReactionSchema, UpdateMessageSchema
from live_chat.web.api.messages.utils import (
    check_parent_message,
    publish_faststream,
    save_message_to_db,
    transformation_message,
    validate_message_schema,
    validate_user_access_to_message,
)
from live_chat.web.api.read_status.utils import increase_in_unread_messages
from live_chat.web.api.users.utils import custom_current_user
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
    return messages


@message_router.post("/chats/{chat_id}/messages")
async def post_message(
    message_schema: PostMessageSchema,
    chat: Chat = Depends(validate_user_access_to_chat),
    current_user: User = Depends(custom_current_user),
    db_session: AsyncSession = Depends(get_async_session),
    _: None = Depends(validate_message_schema),
) -> GetMessageSchema:
    """Post message in FastStream."""
    if chat.chat_type.value == "direct":
        recipient = next(
            (user for user in chat.users if user.id != current_user.id),
            None,
        )
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
        db_session,
        message_schema,
        chat,
        current_user,
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
    message: Message = Depends(validate_user_access_to_message),
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
