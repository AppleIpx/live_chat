from typing import List

from fastapi import HTTPException
from starlette import status

from live_chat.db.models.chat import Chat  # type: ignore[attr-defined]
from live_chat.db.models.messages import Message
from live_chat.db.models.user import User


async def validate_access_to_msg_in_chat(
    from_chat: Chat,
    messages: List[Message | None],
    current_user: User,
) -> None:
    """Checks whether the user has access to the specified messages in a chat."""
    if not from_chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found",
        )
    members_of_chat = [user.id for user in from_chat.users]
    if current_user.id not in members_of_chat:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You have no access to this chat {from_chat.id}",
        )
    for message in messages:
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found, it is none",
            )
        if message.chat_id != from_chat.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Message {message.id} is not from chat {from_chat.id}",
            )
