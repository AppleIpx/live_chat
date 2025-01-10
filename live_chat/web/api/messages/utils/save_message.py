from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.chat import (  # type: ignore[attr-defined]
    Chat,
    DeletedMessage,
    DraftMessage,
    Message,
    User,
)
from live_chat.web.api.chat.utils import set_previous_message_content
from live_chat.web.api.messages import PostMessageSchema
from live_chat.web.api.messages.schemas import (
    PostDraftMessageSchema,
    UpdateMessageSchema,
)


async def save_message_to_db(
    db_session: AsyncSession,
    message_schema: PostMessageSchema,
    chat: Chat,
    current_user: User,
) -> Message | None:
    """Save the message to the database."""
    message_content = message_schema.content
    message = Message(
        content=message_content,
        message_type=message_schema.message_type,
        file_path=message_schema.file_path,
        file_name=message_schema.file_name,
        chat_id=chat.id,
        user_id=current_user.id,
        reactions=[],
    )
    chat.updated_at = datetime.now()
    if message_content is None:
        await set_previous_message_content(chat, db_session)
    else:
        chat.last_message_content = message_content[:100]
    db_session.add_all([message, chat])
    await db_session.commit()
    return message


async def save_deleted_message_to_db(
    db_session: AsyncSession,
    message: Message,
    chat: Chat,
) -> DeletedMessage | None:
    """Save the message to the database."""
    deleted_message = DeletedMessage(
        content=message.content,
        file_name=message.file_name,
        file_path=message.file_path,
        message_type=message.message_type,
        chat_id=message.chat_id,
        user_id=message.user_id,
        original_message_id=message.id,
        is_deleted=True,
    )
    await set_previous_message_content(chat, db_session)
    db_session.add_all([deleted_message, chat])
    await db_session.commit()
    await db_session.refresh(deleted_message)

    return deleted_message


async def save_draft_message_to_db(
    db_session: AsyncSession,
    draft_message_schema: PostDraftMessageSchema,
    chat: Chat,
    current_user: User,
) -> DraftMessage:
    """Helper function to create a new draft message."""
    try:
        draft_message_content = draft_message_schema.content
        draft_message = DraftMessage(
            content=draft_message_content,
            message_type=draft_message_schema.message_type,
            file_path=draft_message_schema.file_path,
            file_name=draft_message_schema.file_name,
            chat_id=chat.id,
            user_id=current_user.id,
        )
        db_session.add(draft_message)
        await db_session.commit()

    except Exception as exc_info:
        await db_session.rollback()
        raise exc_info

    else:
        return draft_message


async def update_draft_message_to_db(
    db_session: AsyncSession,
    draft_message_schema: UpdateMessageSchema,
    draft_message: DraftMessage,
) -> DraftMessage:
    """Helper function to update a draft message."""
    try:
        draft_message.content = draft_message_schema.content
        draft_message.message_type = draft_message_schema.message_type
        draft_message.file_path = draft_message_schema.file_path
        draft_message.file_name = draft_message_schema.file_name
        db_session.add(draft_message)
        await db_session.commit()
    except Exception as exc_info:
        await db_session.rollback()
        raise exc_info

    else:
        return draft_message
