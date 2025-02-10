import logging

from sqladmin._queries import Query
from sqlalchemy import update
from starlette.requests import Request

from live_chat.db.models.user import User


class CustomQuery(Query):
    """Custom SQL Query Class."""

    async def _delete_async(self, pk: str, request: Request) -> None:
        if self.model_view.model == User:
            async with self.model_view.session_maker() as session:
                stmt = update(User).where(User.id == pk).values(is_deleted=True)  # type: ignore[arg-type]
                await session.execute(stmt)
                await session.commit()
        else:
            logging.warning("You're not deleting a User")
