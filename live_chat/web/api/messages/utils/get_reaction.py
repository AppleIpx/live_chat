from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.reaction import Reaction


async def get_reaction_by_message_id_and_user_id(
    db_session: AsyncSession,
    *,
    user_id: UUID,
    message_id: UUID,
) -> Reaction | None:
    """Function to get a reaction by his id from db."""
    query = select(Reaction).where(
        Reaction.user_id == user_id,
        Reaction.message_id == message_id,
    )
    result = await db_session.execute(query)
    return result.scalar_one_or_none()
