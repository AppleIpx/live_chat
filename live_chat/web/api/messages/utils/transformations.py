from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.messages import DraftMessage, Message
from live_chat.web.api.messages.schemas import (
    GetDraftMessageSchema,
    GetForwardMessageSchema,
    GetMessageSchema,
    GetReactionSchema,
)
from live_chat.web.api.users.utils.transformations import (
    transformation_short_user,
)


async def transformation_message(
    message: Message,
    db_session: AsyncSession,
) -> GetMessageSchema:
    """Transform a Message into a GetMessageSchema."""
    reactions = [
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
        forward_message = GetForwardMessageSchema(
            id=message.forwarded_message_id,  # type: ignore[arg-type]
            user=user_schema,
        )
    else:
        forward_message = None
    return GetMessageSchema(
        id=message.id,
        content=message.content,
        created_at=message.created_at,
        updated_at=message.updated_at,
        chat_id=message.chat.id,
        user_id=message.user.id,
        is_deleted=message.is_deleted,
        message_type=message.message_type,
        parent_message_id=message.parent_message_id,
        file_name=message.file_name,
        file_path=message.file_path,
        reactions=reactions,
        forwarded_message=forward_message,
    )


async def transformation_draft_message(
    draft_message: DraftMessage,
) -> GetDraftMessageSchema:
    """Transform a Draft Message into a GetDraftMessageSchema."""
    return GetDraftMessageSchema(
        id=draft_message.id,
        content=draft_message.content,
        created_at=draft_message.created_at,
        updated_at=draft_message.updated_at,
        chat_id=draft_message.chat.id,
        user_id=draft_message.user.id,
        is_deleted=draft_message.is_deleted,
        parent_message_id=draft_message.parent_message_id,
        message_type=draft_message.message_type,
        file_name=draft_message.file_name,
        file_path=draft_message.file_path,
    )


async def transformation_forward_msg(
    forward_messages: List[Message],
    db_session: AsyncSession,
) -> list[GetMessageSchema]:
    """Transform a list of forward messages into GetMessageSchema."""

    result = []
    for forward_message in forward_messages:
        forward_msg_schema = None
        if forward_message.forwarded_message:
            user_schema = transformation_short_user(
                user=forward_message.forwarded_message.user,
            )
            forward_msg_schema = GetForwardMessageSchema(
                id=forward_message.forwarded_message.id,
                user=user_schema,
            )

        result.append(
            GetMessageSchema(
                id=forward_message.id,
                chat_id=forward_message.chat_id,
                user_id=forward_message.user_id,
                content=forward_message.content,
                reactions=[],
                forwarded_message=forward_msg_schema,
                message_type=forward_message.message_type,
                created_at=forward_message.created_at,
                updated_at=forward_message.updated_at,
                is_deleted=forward_message.is_deleted,
                file_name=forward_message.file_name,
                file_path=forward_message.file_path,
                parent_message_id=forward_message.parent_message_id,
            ),
        )

    return result
