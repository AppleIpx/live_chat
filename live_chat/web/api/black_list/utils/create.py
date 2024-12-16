from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.chat import BlackList, User  # type: ignore[attr-defined]


async def create_black_list(
    current_user: User,
    db_session: AsyncSession,
) -> None:
    """Function for creating blacklist."""
    blacklist = BlackList(owner_id=current_user.id)
    db_session.add(blacklist)
    await db_session.commit()
    await db_session.refresh(blacklist)
