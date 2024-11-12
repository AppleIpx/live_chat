import logging

from fastapi import APIRouter, Depends
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.websockets import WebSocket, WebSocketDisconnect

from live_chat.db.utils import get_async_session
from live_chat.services.faststream import fast_stream_router
from live_chat.web.api.messages.schema import ChatMessage, GroupUsage
from live_chat.web.websocket import websocket_manager
from live_chat.web.websocket.enums import WebSocketActionType

websocket_router = APIRouter()
logger = logging.getLogger(__name__)


@websocket_router.websocket("/ws/{username}")
async def websocket_endpoint(
    websocket: WebSocket,
    username: str,
    db_session: AsyncSession = Depends(get_async_session),
) -> None:
    """Create WebSocket connection."""
    await websocket_manager.connect(websocket, username)
    websocket_manager.db_session = db_session
    try:
        while True:
            try:
                data = await websocket.receive_json()
                if (action := data["action_type"]) == WebSocketActionType.SEND_MESSAGE:
                    message = ChatMessage(**data)
                    channel = f"{message.chat_type.value}:{message.chat_id}"
                else:
                    group_usage = GroupUsage(**data)
                    channel = f"{action}:{group_usage.group_id}"
                await fast_stream_router.broker.publish(data, channel)
            except ValidationError as e:
                error_message = {"error": "Invalid data", "details": e.errors()}
                await websocket.send_json(error_message)
    except WebSocketDisconnect:
        logger.info(f"Client {username} disconnected")
    finally:
        websocket_manager.disconnect(username)


@fast_stream_router.subscriber(channel="direct:{chat_id}")
async def receive_message_from_user(
    message: ChatMessage,
    chat_id: str,
) -> None:
    """Processing messages and sending them to the user."""
    if chat_id == message.sender_id:
        await websocket_manager.send_return_message(
            "Вы не можете отправить сообщение себе",
            message.sender_id,
        )
    elif chat_id in websocket_manager.active_connections:
        await websocket_manager.send_direct_message(message.content, chat_id)
    else:
        logger.info("Client is not online")
        # TODO: add sending deferred messages


@fast_stream_router.subscriber(channel="group_join:{group_id}")
async def join_group(
    group_usage: GroupUsage,
    group_id: str,
) -> None:
    """Join a group."""
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
    """Leave the group."""
    user_id = group_usage.sender_id
    await websocket_manager.remove_from_group(user_id, group_id)
    await websocket_manager.send_return_message(
        f"Вы вышли из группы {group_id}",
        user_id,
    )


@fast_stream_router.subscriber(channel="group:{chat_id}")
async def receive_message_from_group(
    message: ChatMessage,
    chat_id: str,
) -> None:
    """Processing messages and sending them to the group."""
    await websocket_manager.send_group_message(message.content, chat_id)
