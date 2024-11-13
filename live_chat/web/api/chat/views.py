from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from live_chat.db.models.chat import Chat, User  # type: ignore[attr-defined]
from live_chat.db.utils import get_async_session
from live_chat.web.api.chat.schemas import CreateDirectChatSchema, DisplayChatSchema
from live_chat.web.api.chat.utils.check_direct_chat_exists import direct_chat_exists
from live_chat.web.api.chat.utils.create_direct_chat import create_direct_chat
from live_chat.web.api.users.utils.check_user_auth import get_current_auth_user
from live_chat.web.api.users.utils.get_user_by_id import get_user_by_id
from live_chat.web.api.users.utils.utils import current_active_user

chat_router = APIRouter()


@chat_router.post(
    "/create/direct/",
    summary="Create a direct chat",
    response_model=DisplayChatSchema,
)
async def create_direct_chat_view(
    create_direct_chat_schema: CreateDirectChatSchema,
    db_session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user),
) -> HTTPException | Chat:
    """Create a new direct chat between the current user and a recipient user.

    This endpoint allows the current user to initiate a direct chat with another user.
    It verifies that the recipient user exists and
    that there is no existing chat between
    the two users before creating a new chat.

    Returns:
        DisplayChatSchema: The newly created chat information,
        serialized according to the response model.
    """
    if get_current_auth_user(user_requesting=current_user):
        # check if another user (recipient) exists
        recipient_user_id = create_direct_chat_schema.recipient_user_id
        recipient_user: User | None = await get_user_by_id(
            db_session,
            user_id=recipient_user_id,
        )

        # must check that recipient user is not the same as initiator
        if not recipient_user:
            return HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"There is no recipient user with id [{recipient_user_id}]",
            )

        if await direct_chat_exists(
            db_session,
            current_user=current_user,
            recipient_user=recipient_user,
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Chat with recipient user exists [{recipient_user_id}]",
            )

        chat: Chat = await create_direct_chat(
            db_session,
            initiator_user=current_user,
            recipient_user=recipient_user,
        )
        return chat

    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="failed to complete the authorization step",
    )
