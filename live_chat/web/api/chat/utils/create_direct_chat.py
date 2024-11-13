from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.chat import (  # type: ignore[attr-defined]
    Chat,
    ReadStatus,
    User,
)
from live_chat.db.models.enums import ChatType


async def create_direct_chat(
    db_session: AsyncSession,
    *,
    initiator_user: User,
    recipient_user: User,
) -> Chat:
    """
    Create a new direct chat between two users and initialize their read status.

    This function creates a direct chat of type ChatType.DIRECT and adds the initiating
    and recipient users to the chat.
    It also creates initial read status records for both users.
    """
    try:
        chat = Chat(chat_type=ChatType.DIRECT)
        chat.users.append(initiator_user)
        chat.users.append(recipient_user)
        new_chat = await db_session.merge(chat)
        db_session.add(new_chat)
        await db_session.flush()

        initiator_read_status = ReadStatus(
            chat_id=new_chat.id,
            user_id=initiator_user.id,
        )
        recipient_read_status = ReadStatus(
            chat_id=new_chat.id,
            user_id=recipient_user.id,
        )
        db_session.add_all([initiator_read_status, recipient_read_status])
        await db_session.commit()

    except Exception as exc_info:
        await db_session.rollback()
        raise exc_info

    else:
        return new_chat
