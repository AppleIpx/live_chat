import uuid
from typing import Any, AsyncGenerator
from unittest.mock import AsyncMock, patch

import pytest
from fakeredis import FakeServer
from fakeredis.aioredis import FakeConnection
from fastapi import FastAPI
from httpx import AsyncClient, Response
from redis.asyncio import ConnectionPool
from sqlalchemy import NullPool
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
from live_chat.web.utils.s3_client import S3Client
from tests.factories import ChatFactory


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

    engine = create_async_engine(
        str(settings.db_url),
        poolclass=NullPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(meta.create_all)

    try:
        yield engine
    finally:
        await engine.dispose()
        await drop_database()


@pytest.fixture
async def clean_database(_engine: AsyncEngine) -> None:
    """Fixture for cleaning the database before each test."""
    from live_chat.db.meta import meta

    async with _engine.begin() as conn:
        for table in reversed(meta.sorted_tables):
            await conn.execute(table.delete())


@pytest.fixture(scope="function")
async def dbsession(
    _engine: AsyncEngine,
    clean_database: None,
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
        bind=connection,
        expire_on_commit=False,
    )
    session = session_maker()

    try:
        yield session
        if trans.is_active:
            await trans.rollback()
            await session.close()
            await connection.close()
    finally:
        await session.close()
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
async def authorized_client(
    client: AsyncClient,
    registered_user: Response,
) -> AsyncClient:
    """Fixture for user registration and authorization."""
    response = await client.post(
        "/api/auth/jwt/login",
        data={
            "username": "user1@example.com",
            "password": "string_123",
        },
    )
    token = response.json().get("access_token")
    client.headers.update({"Authorization": f"Bearer {token}"})
    yield client


@pytest.fixture
async def authorized_deleted_client(
    client: AsyncClient,
    registered_deleted_user: Response,
) -> AsyncClient:
    """Fixture for deleted user registration and authorization."""
    response = await client.post(
        "/api/auth/jwt/login",
        data={
            "username": "user2@example.com",
            "password": "string_123",
        },
    )
    token = response.json().get("access_token")
    client.headers.update({"Authorization": f"Bearer {token}"})
    yield client


@pytest.fixture
async def authorized_banned_client(
    client: AsyncClient,
    registered_banned_user: Response,
) -> AsyncClient:
    """Fixture for banned user registration and authorization."""
    response = await client.post(
        "/api/auth/jwt/login",
        data={
            "username": "user3@example.com",
            "password": "string_123",
        },
    )
    token = response.json().get("access_token")
    client.headers.update({"Authorization": f"Bearer {token}"})
    yield client


@pytest.fixture
def override_get_async_session(
    fastapi_app: FastAPI,
    dbsession: AsyncSession,
) -> AsyncGenerator[None, None]:
    """Overrides the get_async_session dependency to use the session from dbsession."""

    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield dbsession

    fastapi_app.dependency_overrides[get_async_session] = _override_get_db
    yield
    fastapi_app.dependency_overrides.pop(get_async_session, None)


@pytest.fixture
def upload_group_image_mock(group_chat_with_users: ChatFactory) -> AsyncMock:
    """Mock upload file in S3."""
    with patch.object(
        S3Client,
        "upload_file",
        return_value=f"{settings.minio_url}group_images/{group_chat_with_users.id}.png",
    ) as mock_upload:
        yield mock_upload


@pytest.fixture
def upload_chat_attachments_mock(direct_chat_with_users: ChatFactory) -> AsyncMock:
    """Mock upload file in S3."""
    with patch.object(
        S3Client,
        "upload_file",
        return_value=f"{settings.minio_url}chat_attachments/{direct_chat_with_users.id}/{uuid.uuid4()}.png",
    ) as mock_upload:
        yield mock_upload
