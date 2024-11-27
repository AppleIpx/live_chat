from typing import Optional

from fastapi_users.models import UP
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy import func, select


class CustomSQLAlchemyUserDatabase(SQLAlchemyUserDatabase):  # type: ignore[type-arg]
    """Custom Database adapter for SQLAlchemy."""

    async def get_by_username(self, username: str) -> Optional[UP]:
        """
        Get a user by username.

        :param username: username of the user to retrieve.
        :raises UserNotExists: The user does not exist.
        :return: A user.
        """
        statement = select(self.user_table).where(
            func.lower(self.user_table.username) == func.lower(username),
        )
        return await self._get_user(statement)
