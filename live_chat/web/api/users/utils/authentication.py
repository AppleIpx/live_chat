import uuid

from fastapi import Depends, HTTPException, status
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import AuthenticationBackend, BearerTransport

from live_chat.db.models.user import User
from live_chat.web.api.users.utils.dependency import get_jwt_strategy, get_user_manager

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")
auth_jwt = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)
backends = [
    auth_jwt,
]
api_users = FastAPIUsers[User, uuid.UUID](get_user_manager, backends)
current_active_user = api_users.current_user(active=True)


async def custom_current_user(
    user: User = Depends(current_active_user),
) -> User:
    """Checks that the user is not marked as deleted."""
    if user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are deleted.",
        )
    if user.is_banned:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"status": "banned", "reason": user.ban_reason},
        )
    return user
