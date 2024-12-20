from typing import List

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.web.api.users.utils import get_user_by_id
from tests.factories import (
    BlackListFactory,
    BlockedUsersFactory,
    UserFactory,
)
from tests.utils import get_first_black_list_from_db, get_first_user_from_db


@pytest.fixture
async def black_list_owner_auth_user(
    authorized_client: AsyncClient,
    dbsession: AsyncSession,
) -> BlackListFactory:
    """Fixture for generating an empty blacklist whose owner is an authorized user."""
    BlackListFactory._meta.sqlalchemy_session = dbsession  # noqa: SLF001
    auth_user = await get_first_user_from_db(db_session=dbsession)
    return BlackListFactory(owner=auth_user)


@pytest.fixture
async def black_list_owner_random_user(
    authorized_client: AsyncClient,
    user: UserFactory,
    dbsession: AsyncSession,
) -> BlackListFactory:
    """Fixture for generating an empty blacklist whose owner is a random user."""
    BlackListFactory._meta.sqlalchemy_session = dbsession  # noqa: SLF001
    random_user = await get_user_by_id(user_id=user.id, db_session=dbsession)
    return BlackListFactory(owner=random_user)


@pytest.fixture
async def black_list_with_user(
    black_list_owner_auth_user: BlackListFactory,
    user: UserFactory,
    dbsession: AsyncSession,
) -> BlackListFactory:
    """A fixture that blacklists a random user."""
    BlockedUsersFactory._meta.sqlalchemy_session = dbsession  # noqa: SLF001
    black_list_from_db = await get_first_black_list_from_db(db_session=dbsession)
    BlockedUsersFactory(blacklist_id=black_list_from_db.id, user_id=user.id)
    return black_list_owner_auth_user


@pytest.fixture
async def black_list_with_auth_user(
    black_list_owner_random_user: BlackListFactory,
    user: UserFactory,
    dbsession: AsyncSession,
) -> BlackListFactory:
    """A fixture that blacklists a auth user."""
    BlockedUsersFactory._meta.sqlalchemy_session = dbsession  # noqa: SLF001
    auth_user = await get_first_user_from_db(db_session=dbsession)
    black_list_from_db = await get_first_black_list_from_db(db_session=dbsession)
    BlockedUsersFactory(blacklist_id=black_list_from_db.id, user_id=auth_user.id)
    return black_list_owner_random_user


@pytest.fixture
async def black_list_with_users(
    black_list_owner_auth_user: BlackListFactory,
    some_users: List[UserFactory],
    dbsession: AsyncSession,
) -> BlackListFactory:
    """A fixture for generating an empty black list factory."""
    BlockedUsersFactory._meta.sqlalchemy_session = dbsession  # noqa: SLF001
    black_list_from_db = await get_first_black_list_from_db(db_session=dbsession)
    for some_user in some_users:
        BlockedUsersFactory(blacklist_id=black_list_from_db.id, user_id=some_user.id)
    return black_list_owner_auth_user
