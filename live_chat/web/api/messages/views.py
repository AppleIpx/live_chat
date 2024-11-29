import json
import logging
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi_pagination import set_page
from fastapi_pagination.cursor import CursorPage, CursorParams
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette import EventSourceResponse

from live_chat.db.models.chat import Chat, Message, User  # type: ignore[attr-defined]
from live_chat.db.utils import get_async_session
from live_chat.services.faststream import fast_stream_broker
from live_chat.services.redis import redis
from live_chat.web.api.chat.utils import (
    get_chat_by_id,
    get_user_chats,
    validate_user_access_to_chat,
)
from live_chat.web.api.messages.constants import (
    REDIS_CHANNEL_PREFIX,
    REDIS_SSE_KEY_PREFIX,
)
from live_chat.web.api.messages.schemas import (
    GetMessageSchema,
    PostMessageSchema,
    UpdateMessageSchema,
)
from live_chat.web.api.messages.utils import (
    get_user_from_token,
    message_generator,
    save_message_to_db,
    transformation_message,
    validate_user_access_to_message,
)
from live_chat.web.api.messages.utils.delete_message import delete_message_by_id
from live_chat.web.api.messages.utils.get_correct_last_message import (
    get_correct_last_message,
)
from live_chat.web.api.users.user_manager import UserManager
from live_chat.web.api.users.utils import current_active_user, get_user_manager

message_router = APIRouter()
logger = logging.getLogger(__name__)


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
    return await paginate(db_session, query, params=params)


@message_router.get("/chats/{chat_id}/messages/last")
async def get_last_message(
    chat: Chat = Depends(validate_user_access_to_chat),
) -> GetMessageSchema | None:
    """Get the latest message is_deleted=false in chat."""
    last_message = await get_correct_last_message(chat.messages)
    return transformation_message([last_message])[0] if chat.messages else None


@message_router.post("/chats/{chat_id}/messages")
async def post_message(
    message: PostMessageSchema,
    chat: Chat = Depends(validate_user_access_to_chat),
    current_user: User = Depends(current_active_user),
    db_session: AsyncSession = Depends(get_async_session),
) -> dict[str, str]:
    """Post message in FastStream."""
    if created_message := await save_message_to_db(
        db_session,
        message.content,
        chat.id,
        current_user,
    ):
        message_data: GetMessageSchema = transformation_message([created_message])[0]
        for user in chat.users:
            target_channel = f"{REDIS_CHANNEL_PREFIX}:{chat.id!s}:{user.id!s}"
            await fast_stream_broker.publish(
                json.dumps(jsonable_encoder(message_data.model_dump())),
                channel=target_channel,
            )
        return {"status": "Message published"}
    raise HTTPException(
        status_code=404,
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
    message.content = message_schema.content
    db_session.add(message)
    await db_session.commit()
    await db_session.refresh(message)
    return GetMessageSchema(
        id=message.id,
        content=message.content,
        created_at=message.created_at,
        updated_at=message.updated_at,
        chat_id=message.chat.id,
        user_id=message.user.id,
        is_deleted=message.is_deleted,
    )


@message_router.delete(
    "/chats/{chat_id}/messages/{message_id}",
    response_model=None,
)
async def delete_message(
    chat: Chat = Depends(validate_user_access_to_chat),
    message: Message = Depends(validate_user_access_to_message),
    db_session: AsyncSession = Depends(get_async_session),
) -> JSONResponse | Response:
    """Delete message.

    This endpoint implies 2 responses 204 and 202. If a message arrives for the first
    time, then it is assigned is_deleted = true and 202 status is returned, and
    if the message already arrives with this flag(is_deleted = true),
    then status 204 is returned and deleted from the database
    """
    if message.is_deleted:
        await delete_message_by_id(message_id=message.id, db_session=db_session)
        return Response(status_code=204)
    message.is_deleted = True
    db_session.add(message)
    await db_session.commit()
    await db_session.refresh(message)
    return JSONResponse(
        content={"detail": "Сообщение помещено в недавно удаленные"},
        status_code=202,
    )


@fast_stream_broker.subscriber(channel="{REDIS_CHANNEL_PREFIX}:{chat_id}:{user_id}")
async def process_message(message: Any) -> None:
    """Save the message in Redis for SSE subscribers."""
    decoded_message = json.loads(message.body.decode("utf-8"))
    chat_id = message.path["chat_id"]
    user_id = message.path["user_id"]
    redis_key = f"{REDIS_SSE_KEY_PREFIX}{chat_id}_{user_id}"

    await redis.lpush(  # type: ignore[misc]
        redis_key,
        json.dumps(decoded_message, ensure_ascii=False),
    )


@message_router.get("/chats/{chat_id}/events")
async def sse_events(
    chat_id: UUID,
    token: str = Query(..., alias="token"),
    db_session: AsyncSession = Depends(get_async_session),
    user_manager: UserManager = Depends(get_user_manager),
) -> EventSourceResponse:
    """Client connection to SSE."""
    current_user = await get_user_from_token(token, user_manager)
    chat = await get_chat_by_id(db_session, chat_id=chat_id)

    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")

    user_chats = await get_user_chats(db_session, current_user=current_user)

    if chat not in user_chats:
        raise HTTPException(status_code=403, detail="User is not part of the chat")

    redis_key = f"{REDIS_SSE_KEY_PREFIX}{chat.id}_{current_user.id}"
    return EventSourceResponse(message_generator(redis_key), ping=60)
