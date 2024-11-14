from typing import List

from sqlalchemy import Select, and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from live_chat.db.models.chat import Chat, User  # type: ignore[attr-defined]
from live_chat.db.models.enums import ChatType
from live_chat.web.api.chat.schemas import GetChatSchema


def transformation_list_chats(chats: List[Chat]) -> List[GetChatSchema]:
    """Transformation of chats to the desired data type. Used to fixed mypy error."""
    return [
        GetChatSchema(
            chat_id=chat.id,
            chat_type=chat.chat_type,
            created_at=chat.created_at,
            updated_at=chat.updated_at,
            users=chat.users,
        )
        for chat in chats
    ]


async def get_query(current_user: User, chat_type: str) -> Select[tuple[Chat]]:
    """Generates a request to obtain chats in which the current user participates."""
    return (
        select(Chat)
        .where(
            and_(
                Chat.users.contains(current_user),
                Chat.chat_type == chat_type,
            ),
        )
        .options(selectinload(Chat.users))
        .order_by(Chat.updated_at.desc())
    )


async def get_user_chats(
    db_session: AsyncSession,
    *,
    current_user: User,
) -> list[Chat]:
    """Gets a list of chats for the current user."""
    result_direct = await db_session.execute(
        await get_query(current_user, ChatType.DIRECT),  # type: ignore[arg-type]
    )
    result_group = await db_session.execute(
        await get_query(current_user, ChatType.GROUP),  # type: ignore[arg-type]
    )

    chats_direct = list(result_direct.scalars().all())
    chats_group = list(result_group.scalars().all())

    return list(set(chats_direct + chats_group))
