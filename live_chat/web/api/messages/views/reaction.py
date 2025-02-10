from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import JSONResponse

from live_chat.db.models.chat import Chat  # type: ignore[attr-defined]
from live_chat.db.models.messages import Message
from live_chat.db.models.reaction import Reaction
from live_chat.db.models.user import User
from live_chat.db.utils import get_async_session
from live_chat.web.api.chat.utils import validate_user_access_to_chat
from live_chat.web.api.messages.schemas import GetReactionSchema, PostReactionSchema
from live_chat.web.api.messages.utils import (
    delete_reaction_by_id,
    get_reaction_by_message_id_and_user_id,
    publish_faststream,
    validate_message_exists,
)
from live_chat.web.api.users.utils import custom_current_user

reaction_router = APIRouter()


@reaction_router.post("/chats/{chat_id}/messages/{message_id}/reaction")
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


@reaction_router.delete("/chats/{chat_id}/messages/{message_id}/reaction")
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
