from typing import List

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import BlackListFactory, BlockedUsersFactory, UserFactory
from tests.utils import get_first_black_list_from_db, get_first_user_from_db


@pytest.fixture
async def black_list(
    authorized_client: AsyncClient,
    dbsession: AsyncSession,
) -> BlackListFactory:
    """A fixture for generating an empty black list."""
    BlackListFactory._meta.sqlalchemy_session = dbsession  # noqa: SLF001
    auth_user = await get_first_user_from_db(db_session=dbsession)
    return BlackListFactory(owner=auth_user)


@pytest.fixture
async def black_list_with_users(
    black_list: BlackListFactory,
    some_users: List[UserFactory],
    dbsession: AsyncSession,
) -> BlackListFactory:
    """A fixture for generating an empty black list factory."""
    BlockedUsersFactory._meta.sqlalchemy_session = dbsession  # noqa: SLF001
    black_list_from_db = await get_first_black_list_from_db(db_session=dbsession)
    for some_user in some_users:
        BlockedUsersFactory(blacklist_id=black_list_from_db.id, user_id=some_user.id)
    return black_list
