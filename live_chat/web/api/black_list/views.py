from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination.cursor import CursorPage, CursorParams
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from live_chat.db.models.chat import (  # type: ignore[attr-defined]
    BlackList,
    BlockedUsers,
    User,
)
from live_chat.db.utils import get_async_session
from live_chat.web.api.black_list import (
    BlackListCreateSchema,
    BlackListSchema,
)
from live_chat.web.api.black_list.utils import (
    add_user_to_black_list,
    check_user_in_black_list,
    create_black_list,
    get_black_list_by_owner,
    transformation_black_list,
)
from live_chat.web.api.users.schemas import UserRead
from live_chat.web.api.users.utils import current_active_user, get_user_by_id

black_list_router = APIRouter()


@black_list_router.post(
    "/add",
    summary="Add user to black list",
    response_model=BlackListSchema,
    status_code=status.HTTP_201_CREATED,
)
async def add_user_to_black_list_view(
    create_direct_chat_schema: BlackListCreateSchema,
    current_user: User = Depends(current_active_user),
    db_session: AsyncSession = Depends(get_async_session),
) -> BlackListSchema:
    """Add user to black list."""
    try:
        if not (
            black_list := await get_black_list_by_owner(
                current_user=current_user,
                db_session=db_session,
            )
        ):
            await create_black_list(current_user=current_user, db_session=db_session)
        if not (
            black_list_user := await get_user_by_id(
                db_session=db_session,
                user_id=create_direct_chat_schema.user_id,
            )
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No user with this id found",
            )
        if await check_user_in_black_list(
            black_list=black_list,
            user_id_black_list=black_list_user.id,
            db_session=db_session,
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already blocked",
            )
        await add_user_to_black_list(
            black_list=black_list,
            black_list_user=black_list_user,
            db_session=db_session,
        )
    except Exception as err:
        await db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"An error occurred while adding a user to the blacklist, {err}",
        ) from err
    else:
        await db_session.commit()
        return await transformation_black_list(
            black_list=black_list,
            owner_id=current_user.id,
            blocked_user=black_list_user,
        )


@black_list_router.get(
    "/blocked_users",
    summary="Get all black listed users",
    response_model=CursorPage[UserRead],
    status_code=status.HTTP_200_OK,
)
async def get_black_list_users(
    current_user: User = Depends(current_active_user),
    db_session: AsyncSession = Depends(get_async_session),
    params: CursorParams = Depends(),
) -> CursorPage[UserRead]:
    """Getting all users from the black list."""
    blacklist_query = select(BlackList.id).where(BlackList.owner_id == current_user.id)
    result = await db_session.execute(blacklist_query)
    blacklist_id = result.scalar()

    blocked_users_query = (
        select(User)
        .join(BlockedUsers, BlockedUsers.user_id == User.id)
        .where(BlockedUsers.blacklist_id == blacklist_id)
        .order_by(User.id)
    )

    return await paginate(db_session, blocked_users_query, params=params)
