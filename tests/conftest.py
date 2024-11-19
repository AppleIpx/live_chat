import uuid
from typing import Any, AsyncGenerator

import pytest
from fakeredis import FakeServer
from fakeredis.aioredis import FakeConnection
from fastapi import FastAPI
from httpx import AsyncClient, Response
from redis.asyncio import ConnectionPool
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from live_chat.db.dependencies import get_db_session
from live_chat.db.utils import create_database, drop_database, get_async_session
from live_chat.services.redis.dependency import get_redis_pool
from live_chat.settings import settings
from live_chat.web.application import get_app
from tests.factories import ChatFactory, MessageFactory, ReadStatusFactory, UserFactory

registration_payload = {
    "email": "user@example.com",
    "password": "string",
    "is_active": True,
    "is_superuser": False,
    "is_verified": False,
    "first_name": "string",
    "last_name": "string",
    "username": "string",
    "user_image": None,
}


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """
    Backend for anyio pytest plugin.

    :return: backend name.
    """
    return "asyncio"


@pytest.fixture(scope="session")
async def _engine() -> AsyncGenerator[AsyncEngine, None]:
    """
    Create engine and databases.

    :yield: new engine.
    """
    from live_chat.db.meta import meta
    from live_chat.db.models import load_all_models

    load_all_models()

    await create_database()

    engine = create_async_engine(str(settings.db_url))
    async with engine.begin() as conn:
        await conn.run_sync(meta.create_all)

    try:
        yield engine
    finally:
        await engine.dispose()
        await drop_database()


@pytest.fixture
async def dbsession(
    _engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    """
    Get session to database.

    Fixture that returns a SQLAlchemy session with a SAVEPOINT, and the rollback to it
    after the test completes.

    :param _engine: current engine.
    :yields: async session.
    """
    connection = await _engine.connect()
    trans = await connection.begin()

    session_maker = async_sessionmaker(
        connection,
        expire_on_commit=False,
    )
    session = session_maker()

    try:
        yield session
    finally:
        await session.close()
        await trans.rollback()
        await connection.close()


@pytest.fixture
async def test_exchange_name() -> str:
    """
    Name of an exchange to use in tests.

    :return: name of an exchange.
    """
    return uuid.uuid4().hex


@pytest.fixture
async def test_routing_key() -> str:
    """
    Name of routing key to use while binding test queue.

    :return: key string.
    """
    return uuid.uuid4().hex


@pytest.fixture
async def fake_redis_pool() -> AsyncGenerator[ConnectionPool, None]:
    """
    Get instance of a fake redis.

    :yield: FakeRedis instance.
    """
    server = FakeServer()
    server.connected = True
    pool = ConnectionPool(connection_class=FakeConnection, server=server)

    yield pool

    await pool.disconnect()


@pytest.fixture
def fastapi_app(
    dbsession: AsyncSession,
    fake_redis_pool: ConnectionPool,
) -> FastAPI:
    """
    Fixture for creating FastAPI app.

    :return: fastapi app with mocked dependencies.
    """
    application = get_app()
    application.dependency_overrides[get_db_session] = lambda: dbsession
    application.dependency_overrides[get_redis_pool] = lambda: fake_redis_pool
    return application


@pytest.fixture
async def client(
    fastapi_app: FastAPI,
    anyio_backend: Any,
) -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture that creates client for requesting server.

    :param fastapi_app: the application.
    :yield: client for the app.
    """
    async with AsyncClient(app=fastapi_app, base_url="http://test", timeout=2.0) as ac:
        yield ac


@pytest.fixture
async def user(dbsession: AsyncSession) -> UserFactory:
    """A fixture for generating a user factory."""
    UserFactory._meta.sqlalchemy_session = dbsession  # noqa: SLF001
    return UserFactory()


@pytest.fixture
async def some_users(dbsession: AsyncSession) -> UserFactory:
    """A fixture for generating five users factory."""
    UserFactory._meta.sqlalchemy_session = dbsession  # noqa: SLF001
    await dbsession.commit()
    return UserFactory.create_batch(5)


@pytest.fixture
async def chat(dbsession: AsyncSession) -> ChatFactory:
    """A fixture for generating a chat factory."""
    ChatFactory._meta.sqlalchemy_session = dbsession  # noqa: SLF001
    return ChatFactory()


@pytest.fixture
async def message(
    dbsession: AsyncSession,
    user: UserFactory,
    chat: ChatFactory,
) -> MessageFactory:
    """Fixture for creating a message."""
    MessageFactory._meta.sqlalchemy_session = dbsession  # noqa: SLF001
    return MessageFactory(
        user=user,
        chat=chat,
        chat_id=chat.id,
        user_id=user.id,
    )


@pytest.fixture
async def read_status(
    dbsession: AsyncSession,
    user: UserFactory,
    chat: ChatFactory,
) -> ReadStatusFactory:
    """Fixture for creating a read status."""
    ReadStatusFactory._meta.sqlalchemy_session = dbsession  # noqa: SLF001
    return ReadStatusFactory(
        user=user,
        chat=chat,
        user_id=user.id,
        chat_id=chat.id,
    )


@pytest.fixture
async def registered_user(client: AsyncClient) -> Response:
    """Fixture for user registration."""
    return await client.post("/api/auth/register", json=registration_payload)


@pytest.fixture
async def authorized_client(client: AsyncClient) -> AsyncClient:
    """Fixture for user registration and authorization."""
    await client.post("/api/auth/register", json=registration_payload)
    login_payload = {
        "username": "user@example.com",
        "password": "string",
    }
    response = await client.post("/api/auth/jwt/login", data=login_payload)

    token = response.json().get("access_token")
    client.headers.update({"Authorization": f"Bearer {token}"})
    yield client


@pytest.fixture
def override_get_async_session(
    dbsession: AsyncSession,
    fastapi_app: FastAPI,
) -> AsyncGenerator[AsyncSession, None]:
    """Overrides the get_async_session dependency to use the session from dbsession."""

    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield dbsession

    fastapi_app.dependency_overrides[get_async_session] = _override_get_db
    yield
    fastapi_app.dependency_overrides.pop(get_async_session)
