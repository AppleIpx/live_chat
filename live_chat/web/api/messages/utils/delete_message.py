from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.chat import (  # type: ignore[attr-defined]
    Chat,
    DeletedMessage,
    Message,
)
from live_chat.web.api.chat.utils import set_previous_message_content


async def delete_message_by_id(
    db_session: AsyncSession,
    *,
    message: Message | DeletedMessage,
    chat: Chat,
) -> None:
    """Function to delete a message from the database."""
    statements = []

    if isinstance(message, DeletedMessage):
        statements.append(delete(DeletedMessage).where(DeletedMessage.id == message.id))
        statements.append(
            delete(Message).where(Message.id == message.original_message_id),
        )
    else:
        statements.append(delete(Message).where(Message.id == message.id))

    for statement in statements:
        await db_session.execute(statement)

    await set_previous_message_content(chat, db_session)
