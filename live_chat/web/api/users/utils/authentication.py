import uuid

from fastapi_users import FastAPIUsers
from fastapi_users.authentication import AuthenticationBackend, BearerTransport

from live_chat.db.models.chat import User  # type: ignore[attr-defined]
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
