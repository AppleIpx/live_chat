import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.chat import ReadStatus
from live_chat.web.api.chat.utils.get_read_status_by_id import get_read_status_by_id
from tests.factories import ReadStatusFactory


@pytest.mark.anyio
async def test_check_fields_read_status(
    read_status: ReadStatusFactory,
    dbsession: AsyncSession,
) -> None:
    """Checking ReadStatus fields."""
    read_status_db = await get_read_status_by_id(
        read_status_id=read_status.id,
        db_session=dbsession,
    )
    assert read_status.id == read_status_db.id
    assert read_status.updated_at == read_status_db.updated_at
    assert read_status.created_at == read_status_db.created_at
    assert read_status.is_deleted == read_status_db.is_deleted
    assert read_status.user == read_status_db.user
    assert read_status.last_read_message_id == read_status_db.last_read_message_id
    assert read_status.chat == read_status_db.chat


@pytest.mark.anyio
async def test_check_save_read_status(
    read_status: ReadStatusFactory,
    dbsession: AsyncSession,
) -> None:
    """Checking whether the ReadStatus is saved in the db."""
    count = await dbsession.execute(select(func.count(ReadStatus.id)))
    count = count.scalar()
    assert count == 1


@pytest.mark.anyio
async def test_check_readstatus_init(
    read_status: ReadStatusFactory,
) -> None:
    """Checking the string representation of the readstatus."""
    expected_init = (
        f"User: {read_status.user_id}, Message: {read_status.last_read_message_id}"
    )
    assert str(read_status) == expected_init
