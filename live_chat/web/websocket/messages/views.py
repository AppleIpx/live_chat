import logging

from fastapi import APIRouter, Depends
from fastapi_users_db_sqlalchemy import UUID_ID
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.websockets import WebSocket, WebSocketDisconnect

from live_chat.db.utils import get_async_session
from live_chat.services.faststream import fast_stream_router
from live_chat.web.websocket import websocket_manager
from live_chat.web.websocket.enums import (
    WebSocketDisconnectTypes,
    WebSocketMessageActions,
)
from live_chat.web.websocket.schemas import SendMessageWebSocketSchema
from live_chat.web.websocket.utils import get_chat_by_id

websocket_router = APIRouter()
logger = logging.getLogger(__name__)


@websocket_router.websocket("/ws/{username}/{chat_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    username: str,
    chat_id: UUID_ID,
    db_session: AsyncSession = Depends(get_async_session),
) -> None:
    """Create WebSocket connection."""
    if await get_chat_by_id(db_session, chat_id=chat_id):
        await websocket_manager.connect(websocket, username, chat_id)
        websocket_manager.db_session = db_session
        try:
            while True:
                data = await websocket.receive_json()
                action_type = data.get("action_type")
                if action_type == WebSocketMessageActions.SEND_MESSAGE:
                    try:
                        message = SendMessageWebSocketSchema(**data)
                        channel = f"{action_type}:{message.chat.id}"
                        await fast_stream_router.broker.publish(data, channel)
                    except ValidationError as error:
                        await websocket.send_json(
                            {
                                "error_type": "Invalid data",
                                "details": error.errors(),
                            },
                        )
                else:
                    await websocket.send_json({"error_type": "Invalid action_type."})
        except WebSocketDisconnect:
            logger.info(f"Client {username} disconnected")
        finally:
            await websocket_manager.disconnect(
                username,
                chat_id,
                WebSocketDisconnectTypes.DISCONNECT_WEBSOCKET,
            )
    else:
        logger.warning("The chat is not in the database.")


@fast_stream_router.subscriber(channel="message:send:{chat_id}")
async def receive_message(
    message: SendMessageWebSocketSchema,
    chat_id: UUID_ID,
) -> None:
    """Processing messages and sending them to the user."""
    await websocket_manager.send_message(message)


"""
Moved to API

@fast_stream_router.subscriber(channel="group_join:{group_id}")
async def join_group(
    group_usage: GroupUsage,
    group_id: str,
) -> None:
    "Join a group."
    user_id = group_usage.sender_id
    is_added = await websocket_manager.add_to_group(user_id, group_id)
    if is_added:
        await websocket_manager.send_return_message(
            f"Вы присоединились к группе {group_id}",
            user_id,
        )


@fast_stream_router.subscriber(channel="group_remove:{group_id}")
async def remove_group(
    group_usage: GroupUsage,
    group_id: str,
) -> None:
    "Leave the group."
    user_id = group_usage.sender_id
    await websocket_manager.remove_from_group(user_id, group_id)
    await websocket_manager.send_return_message(
        f"Вы вышли из группы {group_id}",
        user_id,
    )
"""
