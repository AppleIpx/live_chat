import logging

from fastapi import APIRouter
from pydantic import ValidationError
from starlette.websockets import WebSocket, WebSocketDisconnect

from live_chat.enums import RecipientType, WebSocketActionType
from live_chat.services.faststream import fast_stream_router
from live_chat.web.api.messages.schema import ChatMessage, GroupUsage
from live_chat.web.websocket_manager import WebSocketManager

router = APIRouter()
logger = logging.getLogger(__name__)
websocket_manager: WebSocketManager = WebSocketManager()


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str) -> None:
    """Подключение WebSocket."""
    await websocket_manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_json()
            action = data["action_type"]
            if action == WebSocketActionType.SEND_MESSAGE:
                try:
                    message = ChatMessage(**data)
                except ValidationError as e:
                    error_message = {"error": "Invalid data", "details": e.errors()}
                    await websocket.send_json(error_message)
                    continue

                if (recipient_type := message.recipient_type) not in frozenset(
                    [RecipientType.GROUP, RecipientType.USER],
                ):
                    await websocket_manager.send_return_message(
                        "Тип сообщения некорректен",
                        user_id,
                    )
                channel = f"{recipient_type.value}:{message.recipient_id}"
            else:
                try:
                    group_usage = GroupUsage(**data)
                except ValidationError as e:
                    error_message = {"error": "Invalid data", "details": e.errors()}
                    await websocket.send_json(error_message)
                    continue
                channel = f"{action}:{group_usage.group_id}"
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
    """Обрабатываем сообщения и отправляем их пользователю."""
    if (recipient_id := message.recipient_id) == message.sender_id:
        await websocket_manager.send_return_message(
            "Вы не можете отправить сообщение себе",
            message.sender_id,
        )
    elif recipient_id in websocket_manager.active_connections:
        await websocket_manager.send_direct_message(message.content, recipient_id)
    else:
        await websocket_manager.send_return_message(
            "Пользователь не найден",
            message.sender_id,
        )


@fast_stream_router.subscriber(channel="group:join:{group_id}")
async def join_group(
    group_usage: GroupUsage,
    group_id: str,
) -> None:
    """Подключиться к группе."""
    user_id = group_usage.sender_id
    is_added = await websocket_manager.add_to_group(user_id, group_id)
    if is_added:
        await websocket_manager.send_return_message(
            f"Вы присоединились к группе {group_id}",
            user_id,
        )


@fast_stream_router.subscriber(channel="group:remove:{group_id}")
async def remove_group(
    message: ChatMessage,
    group_id: str,
) -> None:
    """Выйти из группы."""
    user_id = message.sender_id
    await websocket_manager.remove_from_group(user_id, group_id)
    await websocket_manager.send_return_message(
        f"Вы вышли из группы {group_id}",
        user_id,
    )


@fast_stream_router.subscriber(channel="group:{group_id}")
async def receive_message_from_group(
    message: ChatMessage,
    group_id: str,
) -> None:
    """Обрабатываем сообщения и отправляем их группе."""
    recipient_id = message.recipient_id
    await websocket_manager.send_group_message(message.content, recipient_id)
