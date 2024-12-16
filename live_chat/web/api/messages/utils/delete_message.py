from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.chat import (  # type: ignore[attr-defined]
    Chat,
    DeletedMessage,
    Message,
)


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

    query = (
        select(Message)
        .where(
            Message.chat_id == message.chat_id,
            Message.is_deleted == False,  # noqa: E712
        )
        .order_by(Message.created_at.desc())
        .limit(1)
    )
    prev_message = (await db_session.execute(query)).scalar_one_or_none()
    chat.last_message_content = prev_message.content[:100] if prev_message else None
    await db_session.commit()
