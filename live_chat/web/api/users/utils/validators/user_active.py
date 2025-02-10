from fastapi import HTTPException
from starlette import status

from live_chat.db.models.chat import User  # type: ignore[attr-defined]


async def validate_user_active(user: User) -> None:
    """Validate that the recipient is a valid user."""
    if user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This user has been deleted.",
        )
    if user.is_banned:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This user has been banned.",
        )
