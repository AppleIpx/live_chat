import logging
from datetime import datetime, timezone
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
from starlette import status

from live_chat.db.models.chat import (  # type: ignore[attr-defined]
    Chat,
    DeletedMessage,
    Message,
    Reaction,
    User,
)
from live_chat.db.models.enums import MessageType
from live_chat.db.utils import get_async_session
from live_chat.web.api.black_list.utils import validate_user_in_black_list
from live_chat.web.api.chat.utils import (
    get_chat_by_id,
    get_user_chats,
)
from live_chat.web.api.chat.utils.check_user_in_chat import validate_user_access_to_chat
from live_chat.web.api.messages.constants import (
    REDIS_SSE_KEY_PREFIX,
)
from live_chat.web.api.messages.schemas import (
    GetDeletedMessageSchema,
    GetDraftMessageSchema,
    GetMessageSchema,
    GetReactionSchema,
    PostDraftMessageSchema,
    PostMessageSchema,
    PostReactionSchema,
    UpdateMessageSchema,
)
from live_chat.web.api.messages.utils import (
    delete_reaction_by_id,
    get_reaction_by_message_id_and_user_id,
    get_user_from_token,
    message_generator,
    publish_faststream,
    save_message_to_db,
    transformation_message,
    validate_message_exists,
    validate_message_schema,
    validate_user_access_to_message,
)
from live_chat.web.api.messages.utils.delete_message import delete_message_by_id
from live_chat.web.api.messages.utils.recover_message import restore_message
from live_chat.web.api.messages.utils.save_message import (
    save_deleted_message_to_db,
    save_draft_message_to_db,
)
from live_chat.web.api.messages.utils.transformations import (
    transformation_draft_message,
)
from live_chat.web.api.read_status.utils.increase_in_unread_messages import (
    increase_in_unread_messages,
)
from live_chat.web.api.users.user_manager import UserManager
from live_chat.web.api.users.utils import custom_current_user, get_user_manager

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


@message_router.get("/chats/{chat_id}/deleted-messages")
async def get_deleted_messages(
    chat: Chat = Depends(validate_user_access_to_chat),
    current_user: User = Depends(custom_current_user),
    params: CursorParams = Depends(),
    db_session: AsyncSession = Depends(get_async_session),
) -> CursorPage[GetDeletedMessageSchema]:
    """Get messages in chat by pagination."""
    set_page(CursorPage[GetDeletedMessageSchema])
    query = (
        select(DeletedMessage)
        .where(
            DeletedMessage.chat_id == chat.id,
            DeletedMessage.user_id == current_user.id,
        )
        .order_by(DeletedMessage.created_at.desc())
    )
    return await paginate(db_session, query, params=params)


@message_router.post("/chats/{chat_id}/messages/{message_id}/reaction")
async def post_message_reaction(
    reaction_schema: PostReactionSchema,
    message: Message = Depends(validate_message_exists),
    chat: Chat = Depends(validate_user_access_to_chat),
    current_user: User = Depends(custom_current_user),
    db_session: AsyncSession = Depends(get_async_session),
) -> GetReactionSchema:
    """Post reaction to message."""
    if reaction := await get_reaction_by_message_id_and_user_id(
        db_session,
        user_id=current_user.id,
        message_id=message.id,
    ):
        await delete_reaction_by_id(db_session, reaction=reaction)
    reaction = Reaction(
        reaction_type=reaction_schema.reaction_type,
        user_id=current_user.id,
        message_id=message.id,
    )
    db_session.add(reaction)
    await db_session.commit()
    reaction_data = GetReactionSchema(
        id=reaction.id,
        reaction_type=reaction.reaction_type,
        user_id=reaction.user_id,
        message_id=reaction.message_id,
        updated_at=reaction.updated_at,
    )
    event_data = jsonable_encoder(reaction_data.model_dump())
    await publish_faststream("new_reaction", chat.users, event_data, chat.id)
    return reaction_data


@message_router.delete("/chats/{chat_id}/messages/{message_id}/reaction")
async def delete_message_reaction(
    message: Message = Depends(validate_message_exists),
    chat: Chat = Depends(validate_user_access_to_chat),
    current_user: User = Depends(custom_current_user),
    db_session: AsyncSession = Depends(get_async_session),
) -> JSONResponse:
    """Delete reaction to message."""
    if reaction := await get_reaction_by_message_id_and_user_id(
        db_session,
        user_id=current_user.id,
        message_id=message.id,
    ):
        reaction_data = GetReactionSchema(
            id=reaction.id,
            reaction_type=reaction.reaction_type,
            user_id=reaction.user_id,
            message_id=reaction.message_id,
            updated_at=reaction.updated_at,
        )
        event_data = jsonable_encoder(reaction_data.model_dump())
        await delete_reaction_by_id(db_session, reaction=reaction)
        await publish_faststream("delete_reaction", chat.users, event_data, chat.id)
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Reaction not found",
    )


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
        await validate_user_in_black_list(
            recipient=recipient,
            sender=current_user,
            db_session=db_session,
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
        db_session.add_all([message, chat])
        await db_session.commit()
        message_data = await transformation_message(message)
        event_data = jsonable_encoder(message_data.model_dump())
        await publish_faststream("update_message", chat.users, event_data, chat.id)
        return message_data
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="File message cannot updated",
    )


@message_router.post("/chats/{chat_id}/messages/{message_id}/recover")
async def recover_deleted_message(
    chat: Chat = Depends(validate_user_access_to_chat),
    deleted_message: DeletedMessage = Depends(validate_user_access_to_message),
    db_session: AsyncSession = Depends(get_async_session),
) -> JSONResponse:
    """Recover deleted message."""
    if not isinstance(deleted_message, DeletedMessage):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Instance is not deleted message",
        )
    if message := await restore_message(db_session, deleted_message):
        if message.content:
            chat.last_message_content = message.content[:100]
            await db_session.commit()
        message_data = await transformation_message(message)
        event_data = jsonable_encoder(message_data.model_dump())
        await publish_faststream("recover_message", chat.users, event_data, chat.id)
        return JSONResponse(
            content={"detail": "Message restored"},
            status_code=status.HTTP_200_OK,
        )
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Message not restored",
    )


@message_router.delete(
    "/chats/{chat_id}/messages/{message_id}",
    response_model=None,
)
async def delete_message(
    is_forever: bool = False,
    chat: Chat = Depends(validate_user_access_to_chat),
    message: Message | DeletedMessage = Depends(validate_user_access_to_message),
    db_session: AsyncSession = Depends(get_async_session),
) -> JSONResponse | Response:
    """Delete message.

    This endpoint implies 2 responses 204 and 202. If a message arrives for the first
    time, then it is assigned is_deleted = true and 202 status is returned, and
    if the message already arrives with this flag(is_deleted = true),
    then status 204 is returned and deleted from the database
    """
    event_data = jsonable_encoder({"id": f"{message.id!s}"})
    if message.is_deleted or is_forever:
        await delete_message_by_id(message=message, db_session=db_session, chat=chat)
        await publish_faststream("delete_message", chat.users, event_data, chat.id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    message.is_deleted = True
    if deleted_message := await save_deleted_message_to_db(
        db_session=db_session,
        message=message,
        chat=chat,
    ):
        db_session.add_all([message, deleted_message])
        await db_session.commit()
        await db_session.refresh(message)
        await publish_faststream("delete_message", chat.users, event_data, chat.id)
        return JSONResponse(
            content={"detail": "Message added to recently deleted"},
            status_code=status.HTTP_202_ACCEPTED,
        )
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Error with saving deleted message.",
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found",
        )

    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    user_chats = await get_user_chats(db_session, current_user=current_user)

    if chat not in user_chats:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not part of the chat",
        )

    redis_key = f"{REDIS_SSE_KEY_PREFIX}{chat.id}_{current_user.id}"
    return EventSourceResponse(message_generator(redis_key), ping=60)


@message_router.post(
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
