from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi_pagination import set_page
from fastapi_pagination.cursor import CursorPage, CursorParams
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import JSONResponse, Response

from live_chat.db.models.chat import (  # type: ignore[attr-defined]
    Chat,
    DeletedMessage,
    Message,
    User,
)
from live_chat.db.utils import get_async_session
from live_chat.web.api.chat.utils import validate_user_access_to_chat
from live_chat.web.api.messages.schemas import GetDeletedMessageSchema
from live_chat.web.api.messages.utils import (
    publish_faststream,
    transformation_message,
    validate_user_access_to_message,
)
from live_chat.web.api.messages.utils.delete_message import delete_message_by_id
from live_chat.web.api.messages.utils.recover_message import restore_message
from live_chat.web.api.messages.utils.save_message import save_deleted_message_to_db
from live_chat.web.api.users.utils import custom_current_user

deleted_msg_router = APIRouter()


@deleted_msg_router.get("/chats/{chat_id}/deleted-messages")
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


@deleted_msg_router.post("/chats/{chat_id}/messages/{message_id}/recover")
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


@deleted_msg_router.delete(
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
