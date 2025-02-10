from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from live_chat.db.models.chat import Chat  # type: ignore[attr-defined]
from live_chat.db.models.user import User
from live_chat.web.api.read_status.utils import get_read_status_by_user_chat_ids


async def increase_in_unread_messages(
    chat: Chat,
    current_user: User,
    db_session: AsyncSession,
) -> None:
    """Helper function that increments the unread message counter for each users."""
    recipients = [user for user in chat.users if user.id != current_user.id]
    for recipient in recipients:
        if read_status := await get_read_status_by_user_chat_ids(
            db_session=db_session,
            chat_id=chat.id,
            user_id=recipient.id,
        ):
            read_status.count_unread_msg += 1
            db_session.add(read_status)

        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"There is no read_status for user with id [{recipient.id}]",
            )
    await db_session.commit()
