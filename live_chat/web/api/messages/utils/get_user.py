from fastapi import HTTPException
from starlette import status

from live_chat.db.models.chat import User  # type: ignore[attr-defined]
from live_chat.web.api.users.user_manager import UserManager
from live_chat.web.api.users.utils import get_jwt_strategy


async def get_user_from_token(
    token: str,
    user_manager: UserManager,
) -> User:
    """Extract user from JWT token."""
    try:
        jwt_strategy = get_jwt_strategy()
        return await jwt_strategy.read_token(token, user_manager)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        ) from e
