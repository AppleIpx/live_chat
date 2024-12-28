from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi_pagination.cursor import CursorPage, CursorParams
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import JSONResponse

from live_chat.db.models.chat import (  # type: ignore[attr-defined]
    BlockedUsers,
    User,
)
from live_chat.db.utils import get_async_session
from live_chat.web.api.black_list import (
    BlackListCreateSchema,
    BlackListDeleteSchema,
    BlackListSchema,
)
from live_chat.web.api.black_list.utils import (
    add_user_to_black_list,
    create_black_list,
    delete_user_from_black_list,
    get_black_list_by_owner,
)
from live_chat.web.api.black_list.utils.transformation import transformation_black_list
from live_chat.web.api.users.schemas import UserShortRead
from live_chat.web.api.users.utils import custom_current_user, get_user_by_id

black_list_router = APIRouter()


@black_list_router.post(
    "",
    summary="Add user to black list",
    response_model=BlackListSchema,
    status_code=status.HTTP_201_CREATED,
)
async def add_user_to_black_list_view(
    add_user_in_black_list_schema: BlackListCreateSchema,
    current_user: User = Depends(custom_current_user),
    db_session: AsyncSession = Depends(get_async_session),
) -> BlackListSchema:
    """Add user to black list."""
    if not (
        black_list := await get_black_list_by_owner(
            owner=current_user,
            db_session=db_session,
        )
    ):
        black_list = await create_black_list(
            current_user=current_user,
            db_session=db_session,
        )
    if not (
        black_list_user := await get_user_by_id(
            db_session=db_session,
            user_id=add_user_in_black_list_schema.user_id,
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No user with this id found",
        )
    if add_user_in_black_list_schema.user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="It is impossible to add yourself to the blacklist",
        )
    await add_user_to_black_list(
        black_list=black_list,
        black_list_user=black_list_user,
        db_session=db_session,
    )
    await db_session.commit()
    return await transformation_black_list(
        black_list=black_list,
        owner_id=current_user.id,
        blocked_user=black_list_user,
    )


@black_list_router.delete(
    "",
    summary="Delete user from black list",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user_from_black_list_view(
    delete_user_from_black_list_schema: BlackListDeleteSchema,
    current_user: User = Depends(custom_current_user),
    db_session: AsyncSession = Depends(get_async_session),
) -> Response:
    """Delete user from black list."""
    if not (
        black_list := await get_black_list_by_owner(
            owner=current_user,
            db_session=db_session,
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Black list not found",
        )
    if not (
        black_list_user := await get_user_by_id(
            db_session=db_session,
            user_id=delete_user_from_black_list_schema.user_id,
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No user with this id found",
        )
    await delete_user_from_black_list(
        black_list_user=black_list_user,
        black_list=black_list,
        db_session=db_session,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@black_list_router.get(
    "",
    summary="Get all black listed users",
    response_model=CursorPage[UserShortRead],
    status_code=status.HTTP_200_OK,
)
async def get_black_list_users(
    current_user: User = Depends(custom_current_user),
    db_session: AsyncSession = Depends(get_async_session),
    params: CursorParams = Depends(),
) -> CursorPage[UserShortRead] | JSONResponse:
    """Getting all users from the black list."""
    if black_list := await get_black_list_by_owner(
        owner=current_user,
        db_session=db_session,
    ):
        blocked_users_query = (
            select(User)
            .join(BlockedUsers, BlockedUsers.user_id == User.id)
            .where(BlockedUsers.blacklist_id == black_list.id)
            .order_by(User.id)
        )
        return await paginate(db_session, blocked_users_query, params=params)
    return JSONResponse(content=[], status_code=status.HTTP_200_OK)
