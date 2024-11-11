import uuid

from fastapi import Depends
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.dependencies import get_db_session
from live_chat.db.models.chat import User  # type: ignore[attr-defined]
from live_chat.settings import settings
from live_chat.web.api.users.schemas import UserManager


async def get_user_db(  # type: ignore[misc]
    session: AsyncSession = Depends(get_db_session),
) -> SQLAlchemyUserDatabase:  # type: ignore[type-arg]
    """
    Yield a SQLAlchemyUserDatabase instance.

    :param session: asynchronous SQLAlchemy session.
    :yields: instance of SQLAlchemyUserDatabase.
    """
    yield SQLAlchemyUserDatabase(session, User)


async def get_user_manager(  # type: ignore[misc]
    user_db: SQLAlchemyUserDatabase = Depends(get_user_db),  # type: ignore[type-arg]
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


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")
auth_jwt = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)
backends = [
    auth_jwt,
]
api_users = FastAPIUsers[User, uuid.UUID](get_user_manager, backends)
current_active_user = api_users.current_user(active=True)
