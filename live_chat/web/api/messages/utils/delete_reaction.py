from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.chat import Reaction  # type: ignore[attr-defined]


async def delete_reaction_by_id(
    db_session: AsyncSession,
    *,
    reaction: Reaction,
) -> None:
    """Function to delete a reaction from the database."""
    query = delete(Reaction).where(Reaction.id == reaction.id)
    await db_session.execute(query)
    await db_session.commit()
