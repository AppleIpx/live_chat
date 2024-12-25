from live_chat.db.models.chat import Message  # type: ignore[attr-defined]
from live_chat.web.api.messages import GetMessageSchema
from live_chat.web.api.messages.schemas import GetReactionSchema


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
        file_name=message.file_name,
        file_path=message.file_path,
        reactions=reactions,
    )
