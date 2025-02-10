import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.messages import DeletedMessage
from live_chat.web.api.chat.utils import get_deleted_message_by_id
from tests.factories import DeletedMessageFactory


@pytest.mark.anyio
async def test_check_fields_message(
    deleted_message: DeletedMessageFactory,
    dbsession: AsyncSession,
) -> None:
    """Checking deleted message fields."""
    deleted_message_db = await get_deleted_message_by_id(
        deleted_message_id=deleted_message.id,
        db_session=dbsession,
    )
    assert deleted_message.id == deleted_message_db.id
    assert deleted_message.message_type == deleted_message_db.message_type
    assert deleted_message.updated_at == deleted_message_db.updated_at
    assert deleted_message.is_deleted == deleted_message_db.is_deleted
    assert deleted_message.updated_at == deleted_message_db.updated_at
    assert deleted_message.user == deleted_message_db.user
    assert deleted_message.user_id == deleted_message_db.user_id
    assert deleted_message.content == deleted_message_db.content
    assert deleted_message.file_name == deleted_message_db.file_name
    assert deleted_message.file_path == deleted_message_db.file_path


@pytest.mark.anyio
async def test_check_save_message(
    deleted_message: DeletedMessageFactory,
    dbsession: AsyncSession,
) -> None:
    """Checking whether the deleted message is saved in the db."""
    count = await dbsession.execute(select(func.count(DeletedMessage.id)))
    assert count.scalar() == 1


@pytest.mark.anyio
async def test_check_message_init(deleted_message: DeletedMessageFactory) -> None:
    """Checking the string representation of the deleted message."""
    expected_init = (
        f"Deleted message from {deleted_message.user_id} - "
        f"{deleted_message.chat_id} - {deleted_message.created_at}"
    )
    assert str(deleted_message) == expected_init
