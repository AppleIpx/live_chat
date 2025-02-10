from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.black_list import BlackList
from live_chat.db.models.user import User


async def create_black_list(
    current_user: User,
    db_session: AsyncSession,
) -> BlackList:
    """Function for creating blacklist."""
    blacklist = BlackList(owner_id=current_user.id)
    db_session.add(blacklist)
    await db_session.commit()
    await db_session.refresh(blacklist)
    return blacklist
