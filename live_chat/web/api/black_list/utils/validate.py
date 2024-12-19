from typing import List

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from live_chat.db.models.chat import User  # type: ignore[attr-defined]
from live_chat.web.api.black_list.utils import get_black_list_by_owner
from live_chat.web.api.black_list.utils.blocked_users import get_blocked_users


async def validate_user_in_black_list(
    sender: User,
    recipient: User,
    db_session: AsyncSession,
) -> None:
    """
    Validate that users are not in each other's blacklists.

    This function checks the blacklists of the sender and recipient
    and issues an appropriate error if it fails to find any matches.
    """

    black_list_recipient = await get_black_list_by_owner(
        owner=recipient,
        db_session=db_session,
    )
    black_list_sender = await get_black_list_by_owner(
        owner=sender,
        db_session=db_session,
    )

    blocked_users_recipient: List[User] = (
        await get_blocked_users(black_list=black_list_recipient, db_session=db_session)
        if black_list_recipient
        else []
    )
    blocked_users_sender: List[User] = (
        await get_blocked_users(black_list=black_list_sender, db_session=db_session)
        if black_list_sender
        else []
    )
    if any(user.id == recipient.id for user in blocked_users_sender):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can't perform this action, because he's blocked",
        )

    if any(user.id == sender.id for user in blocked_users_recipient):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can't perform this action, you are on the black list",
        )
