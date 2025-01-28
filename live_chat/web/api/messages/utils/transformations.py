from live_chat.db.models.chat import DraftMessage, Message  # type: ignore[attr-defined]
from live_chat.web.api.messages.schemas import (
    GetDraftMessageSchema,
    GetMessageSchema,
    GetReactionSchema,
)


async def transformation_message(message: Message) -> GetMessageSchema:
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
