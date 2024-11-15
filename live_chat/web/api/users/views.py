from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.security import HTTPBearer
from fastapi_users import models
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from live_chat.db.models.chat import User  # type: ignore[attr-defined]
from live_chat.db.utils import get_async_session
from live_chat.web.api.users.schemas import (
    ListUserSchema,
    UserCreate,
    UserRead,
    UserUpdate,
)
from live_chat.web.api.users.utils.get_list_users import (
    get_all_users,
    transformation_users,
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
    users_data = transformation_users(users)
    return ListUserSchema(users=users_data)


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
    image_url = await image_saver.save_user_image(uploaded_image)
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
