from uuid import UUID

from live_chat.db.models.black_list import BlackList
from live_chat.db.models.user import User
from live_chat.web.api.black_list.schemas import BlackListSchema
from live_chat.web.api.users.schemas import UserShortRead


async def transformation_black_list(
    black_list: BlackList,
    owner_id: UUID,
    blocked_user: User,
) -> BlackListSchema:
    """Transform a Black List objects into a BlackListSchema."""
    blocked_user_schema = UserShortRead(
        id=blocked_user.id,
        first_name=blocked_user.first_name,  # type: ignore[call-arg]
        last_name=blocked_user.last_name,  # type: ignore[call-arg]
        username=blocked_user.username,  # type: ignore[call-arg]
        user_image=blocked_user.user_image,  # type: ignore[call-arg]
        last_online=blocked_user.last_online,  # type: ignore[call-arg]
        is_deleted=blocked_user.is_deleted,  # type: ignore[call-arg]
        is_banned=blocked_user.is_banned,  # type: ignore[call-arg]
    )
    return BlackListSchema(
        id=black_list.id,
        owner_id=owner_id,
        blocked_user=blocked_user_schema,
    )
