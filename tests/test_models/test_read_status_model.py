from typing import AsyncGenerator

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.chat import ReadStatus
from tests.factories import ReadStatusFactory


@pytest.mark.anyio
class TestReadStatus:
    """Testing the ReadStatus model."""

    async def test_check_fields_read_status(
        self,
        create_read_status: ReadStatusFactory,
    ) -> None:
        """Checking ReadStatus fields."""
        read_status = create_read_status
        expected_attributes = {
            "id": read_status.id,
            "created_at": read_status.created_at,
            "updated_at": read_status.updated_at,
            "is_deleted": read_status.is_deleted,
            "last_read_message_id": read_status.last_read_message_id,
            "user": read_status.user,
            "chat": read_status.chat,
        }
        for attr, expected_value in expected_attributes.items():
            assert getattr(read_status, attr) == expected_value

    async def test_check_save_read_status(
        self,
        create_read_status: ReadStatusFactory,
        dbsession: AsyncGenerator[AsyncSession, None],
    ) -> None:
        """Checking whether the ReadStatus is saved in the db."""
        _ = create_read_status
        count = await dbsession.execute(select(func.count(ReadStatus.id)))
        count = count.scalar()
        assert count == 1

    async def test_check_readstatus_init(
        self,
        create_read_status: ReadStatusFactory,
    ) -> None:
        """Checking the string representation of the readstatus."""
        read_status = create_read_status
        expected_init = (
            f"User: {read_status.user_id}, Message: {read_status.last_read_message_id}"
        )
        assert str(read_status) == expected_init
