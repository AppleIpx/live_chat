from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.chat import User  # type: ignore[attr-defined]
from live_chat.web.api.users.schemas import UserRead


def transformation_users(users: List[User]) -> list[UserRead]:
    """Transformation of users to the desired data type. Used to fixed mypy error."""
    return [
        UserRead(
            id=user.id,
            email=user.email,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            is_verified=user.is_verified,
            first_name=user.first_name,  # type: ignore[call-arg]
            last_name=user.last_name,  # type: ignore[call-arg]
            username=user.username,  # type: ignore[call-arg]
            user_image=user.user_image,  # type: ignore[call-arg]
        )
        for user in users
    ]


async def get_all_users(
    db_session: AsyncSession,
) -> list[User]:
    """Getting all users from the database."""
    query = (select(User).order_by(User.username)).order_by(User.username)
    result = await db_session.execute(query)

    users: list[User] = list(result.scalars().all())

    return users
