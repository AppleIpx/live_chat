from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.chat import User  # type: ignore[attr-defined]
from live_chat.db.utils import get_async_session
from live_chat.web.api.users.schemas import (
    ListUserSchema,
    UserCreate,
    UserRead,
    UserUpdate,
)
from live_chat.web.api.users.utils.get_list_users import get_all_users, transformation
from live_chat.web.api.users.utils.utils import api_users, auth_jwt

http_bearer = HTTPBearer(auto_error=False)
router = APIRouter(dependencies=[Depends(http_bearer)])

router.include_router(
    api_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

router.include_router(
    api_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)

router.include_router(
    api_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)

router.include_router(
    api_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)
router.include_router(
    api_users.get_auth_router(auth_jwt),
    prefix="/auth/jwt",
    tags=["auth"],
)


@router.get(
    "/users",
    tags=["users"],
    summary="Get all users",
    response_model=ListUserSchema,
)
async def get_users(
    db_session: AsyncSession = Depends(get_async_session),
) -> ListUserSchema:
    """Gets a list of all users."""
    users: list[User] = await get_all_users(db_session)
    users_data = transformation(users)
    return ListUserSchema(users=users_data)
