from sqlalchemy import Select, and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from live_chat.db.models.chat import Chat, User  # type: ignore[attr-defined]
from live_chat.db.models.enums import ChatType


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
