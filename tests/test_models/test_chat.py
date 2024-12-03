from typing import AsyncGenerator

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.chat import Chat
from live_chat.web.api.chat.utils import get_chat_by_id
from tests.factories import ChatFactory


@pytest.mark.anyio
async def test_check_fields_chat(
    chat: ChatFactory,
    dbsession: AsyncSession,
) -> None:
    """Checking chat fields."""
    chat_db = await get_chat_by_id(chat_id=chat.id, db_session=dbsession)
    assert chat.id == chat_db.id
    assert chat.chat_type == chat_db.chat_type
    assert chat.updated_at == chat_db.updated_at
    assert chat.created_at == chat_db.created_at


@pytest.mark.anyio
async def test_check_save_chat(
    chat: ChatFactory,
    dbsession: AsyncSession,
) -> None:
    """Checking whether the chat is saved in the db."""
    count = await dbsession.execute(select(func.count(Chat.id)))
    assert count.scalar() == 1


@pytest.mark.anyio
async def test_check_chat_init(
    chat: ChatFactory,
    dbsession: AsyncGenerator[AsyncSession, None],
) -> None:
    """Checking the string representation of the chat."""
    expected_init = f"{chat.chat_type.value.title()} {chat.id}"
    assert str(chat) == expected_init
