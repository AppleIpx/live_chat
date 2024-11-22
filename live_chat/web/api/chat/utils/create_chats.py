from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.chat import (  # type: ignore[attr-defined]
    Chat,
    ReadStatus,
    User,
)
from live_chat.db.models.enums import ChatType
from live_chat.web.api.chat.schemas import CreateGroupChatSchema


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
    initiator_user = await db_session.get(User, initiator_user.id)
    recipient_user = await db_session.get(User, recipient_user.id)

    try:
        chat = Chat(chat_type=ChatType.DIRECT)
        chat.users.append(initiator_user)
        chat.users.append(recipient_user)
        db_session.add(chat)
        await db_session.flush()

        initiator_read_status = ReadStatus(
            chat_id=chat.id,
            user_id=initiator_user.id,
        )
        recipient_read_status = ReadStatus(
            chat_id=chat.id,
            user_id=recipient_user.id,
        )
        db_session.add_all([initiator_read_status, recipient_read_status])
        await db_session.commit()

    except Exception as exc_info:
        await db_session.rollback()
        raise exc_info

    else:
        return chat


async def create_group_chat(
    db_session: AsyncSession,
    *,
    initiator_user: User,
    recipient_users: List[User],
    create_group_chat_schema: CreateGroupChatSchema,
) -> Chat:
    """Create group chat."""
    initiator_user = await db_session.get(User, initiator_user.id)
    recipient_users = [
        await db_session.get(
            User,
            recipient_user.id,
        )
        for recipient_user in recipient_users
    ]
    try:
        chat = Chat(
            chat_type=ChatType.GROUP,
            name=create_group_chat_schema.name_group,
            image=create_group_chat_schema.image_group,
        )
        chat.users.append(initiator_user)
        for recipient_user in recipient_users:
            chat.users.append(recipient_user)
        db_session.add(chat)
        await db_session.flush()

        initiator_read_status = ReadStatus(
            chat_id=chat.id,
            user_id=initiator_user.id,
        )

        recipients_read_status = [
            ReadStatus(
                chat_id=chat.id,
                user_id=recipient_user.id,
            )
            for recipient_user in recipient_users
        ]

        db_session.add_all([initiator_read_status, *recipients_read_status])
        await db_session.commit()

    except Exception as exc_info:
        await db_session.rollback()
        raise exc_info

    else:
        return chat
