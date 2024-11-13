from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.chat import Chat, User  # type: ignore[attr-defined]
from live_chat.db.models.enums import ChatType


async def direct_chat_exists(
    db_session: AsyncSession,
    *,
    current_user: User,
    recipient_user: User,
) -> bool:
    """Check direct chat exists between the current user and the recipient user."""
    query = select(Chat.id).where(
        and_(
            Chat.chat_type == ChatType.DIRECT,
            Chat.is_deleted.is_(False),
            Chat.users.contains(current_user),
            Chat.users.contains(recipient_user),
        ),
    )
    result = await db_session.execute(query)
    existing_chat = result.scalar_one_or_none()
    return existing_chat is not None
