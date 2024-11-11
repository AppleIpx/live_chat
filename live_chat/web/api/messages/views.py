import logging

from fastapi import APIRouter
from starlette.websockets import WebSocket, WebSocketDisconnect

from live_chat.enums import WebSocketActionType
from live_chat.services.faststream import fast_stream_router
from live_chat.web.api.messages.schema import ChatMessage, GroupUsage
from live_chat.web.utils import validate_model
from live_chat.web.websocket import websocket_manager

websocket_router = APIRouter()
logger = logging.getLogger(__name__)


@websocket_router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str) -> None:
    """Create WebSocket connection."""
    await websocket_manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_json()
            if (action := data["action_type"]) == WebSocketActionType.SEND_MESSAGE:
                message = await validate_model(websocket, ChatMessage, data)
                message_type = message.recipient_type.value  # type: ignore[attr-defined]
                recipient_id = message.recipient_id  # type: ignore[attr-defined]
                channel = f"{message_type}:{recipient_id}"
            else:
                group_usage = await validate_model(websocket, GroupUsage, data)
                group_id = group_usage.group_id  # type: ignore[attr-defined]
                channel = f"{action}:{group_id}"
            await fast_stream_router.broker.publish(data, channel)
    except WebSocketDisconnect:
        logger.info(f"Client {user_id} disconnected")
    finally:
        websocket_manager.disconnect(user_id)


@fast_stream_router.subscriber(channel="user:{user_id}")
async def receive_message_from_user(
    message: ChatMessage,
    user_id: str,
) -> None:
    """Processing messages and sending them to the user."""
    if user_id == message.sender_id:
        await websocket_manager.send_return_message(
            "Вы не можете отправить сообщение себе",
            message.sender_id,
        )
    elif user_id in websocket_manager.active_connections:
        await websocket_manager.send_direct_message(message.content, user_id)
    else:
        await websocket_manager.send_return_message(
            "Пользователь не найден",
            message.sender_id,
        )


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


@fast_stream_router.subscriber(channel="group:{recipient_id}")
async def receive_message_from_group(
    message: ChatMessage,
    recipient_id: str,
) -> None:
    """Processing messages and sending them to the group."""
    await websocket_manager.send_group_message(message.content, recipient_id)
