from fastapi import Depends
from fastapi_users.authentication import JWTStrategy
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.dependencies import get_db_session
from live_chat.db.models.chat import User  # type: ignore[attr-defined]
from live_chat.settings import settings
from live_chat.web.api.users.user_manager import UserManager
from live_chat.web.api.users.utils.custom_user_db import CustomSQLAlchemyUserDatabase


async def get_user_db(  # type: ignore[misc]
    session: AsyncSession = Depends(get_db_session),
) -> CustomSQLAlchemyUserDatabase:  # type: ignore[type-arg]
    """
    Yield a SQLAlchemyUserDatabase instance.

    :param session: asynchronous SQLAlchemy session.
    :yields: instance of SQLAlchemyUserDatabase.
    """
    yield CustomSQLAlchemyUserDatabase(session, User)


async def get_user_manager(  # type: ignore[misc]
    user_db: CustomSQLAlchemyUserDatabase = Depends(get_user_db),  # type: ignore[type-arg]
) -> UserManager:
    """
    Yield a UserManager instance.

    :param user_db: SQLAlchemy user db instance
    :yields: an instance of UserManager.
    """
    yield UserManager(user_db)


def get_jwt_strategy() -> JWTStrategy:  # type: ignore[type-arg]
    """
    Return a JWTStrategy in order to instantiate it dynamically.

    :returns: instance of JWTStrategy with provided settings.
    """
    return JWTStrategy(secret=settings.users_secret, lifetime_seconds=None)
