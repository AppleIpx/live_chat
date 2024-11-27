from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.security import HTTPBearer
from fastapi_pagination import set_page
from fastapi_pagination.cursor import CursorPage, CursorParams
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_users import models
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from live_chat.db.models.chat import User  # type: ignore[attr-defined]
from live_chat.db.utils import get_async_session
from live_chat.web.api.users.schemas import (
    UserCreate,
    UserRead,
    UserUpdate,
)
from live_chat.web.api.users.utils.image_saver import ImageSaver
from live_chat.web.api.users.utils.utils import (
    api_users,
    auth_jwt,
    current_active_user,
    get_user_by_id,
)

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


@router.get("/users", tags=["users"], summary="Get all users")
async def get_users(
    db_session: AsyncSession = Depends(get_async_session),
    params: CursorParams = Depends(),
) -> CursorPage[UserRead]:
    """Gets a list of all users."""
    set_page(CursorPage[UserRead])
    return await paginate(db_session, select(User).order_by(User.id), params=params)


@router.get("/users/read/{user_id}", response_model=UserRead, tags=["users"])
async def get_user(user_id: UUID, user: models.UP = Depends(get_user_by_id)) -> User:
    """Gets a user by id without authentication."""
    return user


@router.patch("/users/me/upload-image", tags=["users"])
async def upload_user_image(
    uploaded_image: UploadFile,
    user: User = Depends(current_active_user),
    db_session: AsyncSession = Depends(get_async_session),
) -> dict[str, str]:
    """Update a user avatar."""
    image_saver = ImageSaver(user.id)
    image_url = await image_saver.save_image(uploaded_image, "avatars")
    if not image_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image upload",
        )

    user.user_image = image_url
    existing_user = await db_session.merge(user)
    db_session.add(existing_user)
    await db_session.commit()
    return {"image_url": image_url}
