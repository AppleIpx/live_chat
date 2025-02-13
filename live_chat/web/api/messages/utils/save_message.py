from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.chat import Chat  # type: ignore[attr-defined]
from live_chat.db.models.enums import MessageType
from live_chat.db.models.messages import (
    DeletedMessage,
    DraftMessage,
    Message,
)
from live_chat.db.models.user import User
from live_chat.web.api.chat.utils import set_previous_message_content
from live_chat.web.api.messages.schemas import (
    PostDraftMessageSchema,
    UpdateMessageSchema,
)


async def save_message_to_db(
    db_session: AsyncSession,
    chat: Chat,
    message_type: MessageType,
    owner_msg_id: UUID,
    content: str | None = None,
    parent_message_id: UUID | None = None,
    file_path: str | None = None,
    file_name: str | None = None,
) -> Message:
    """Function to save messages without forwarded messages in the database."""
    message = Message(
        content=content,
        message_type=message_type,
        parent_message_id=parent_message_id,
        file_path=file_path,
        file_name=file_name,
        chat_id=chat.id,
        user_id=owner_msg_id,
        reactions=[],
    )
    chat.updated_at = datetime.now()
    if content is None:
        await set_previous_message_content(chat, db_session)
    else:
        chat.last_message_content = content[:100]
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


async def save_forwarded_message(
    db_session: AsyncSession,
    orig_messages: list[Message | None],
    to_chat: Chat,
    current_user: User,
) -> list[Message]:
    """Function that creates copy of the message in another chat and adds sent data."""
    forwarded_messages = []
    for orig_msg in orig_messages:
        if orig_msg is not None:
            new_message = Message(
                content=orig_msg.content,
                message_type=orig_msg.message_type,
                parent_message_id=orig_msg.parent_message_id,
                file_path=orig_msg.file_path,
                file_name=orig_msg.file_name,
                chat_id=to_chat.id,
                user_id=current_user.id,
                reactions=[],
                forwarded_message_id=orig_msg.id,
            )
            if orig_msg.content is None:
                await set_previous_message_content(to_chat, db_session)
            else:
                to_chat.last_message_content = orig_msg.content[:100]
            db_session.add_all([new_message, to_chat])
            await db_session.commit()
            forwarded_messages.append(new_message)
    return forwarded_messages
