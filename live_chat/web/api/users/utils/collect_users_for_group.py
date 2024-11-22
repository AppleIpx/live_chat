from typing import List
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from live_chat.db.models.chat import User  # type: ignore[attr-defined]
from live_chat.web.api.users.utils.get_user_by_id import get_user_by_id


async def collect_users_for_group(
    recipient_users_id: List[UUID],
    db_session: AsyncSession,
) -> List[User]:
    """Helper function for collecting users into a group."""
    recipient_users: List[User] = []
    for recipient_user_id in recipient_users_id:
        user = await get_user_by_id(
            db_session=db_session,
            user_id=recipient_user_id,
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"There is no recipient user with id [{recipient_user_id}]",
            )
        recipient_users.append(user)
    return recipient_users
