from uuid import UUID

from live_chat.db.models.chat import BlackList, User  # type: ignore[attr-defined]
from live_chat.web.api.black_list import BlackListSchema
from live_chat.web.api.users.schemas import UserRead


async def transformation_black_list(
    black_list: BlackList,
    owner_id: UUID,
    blocked_user: User,
) -> BlackListSchema:
    """Transform a Black List objects into a BlackListSchema."""
    blocked_user_schema = UserRead(
        id=blocked_user.id,
        email=blocked_user.email,
        first_name=blocked_user.first_name,  # type: ignore[call-arg]
        last_name=blocked_user.last_name,  # type: ignore[call-arg]
        username=blocked_user.username,  # type: ignore[call-arg]
        user_image=blocked_user.user_image,  # type: ignore[call-arg]
        is_active=blocked_user.is_active,
        is_superuser=blocked_user.is_superuser,
        is_verified=blocked_user.is_verified,
    )
    return BlackListSchema(
        id=black_list.id,
        owner_id=owner_id,
        blocked_user=blocked_user_schema,
    )
