import logging

from fastapi import APIRouter
from starlette.websockets import WebSocket, WebSocketDisconnect

from live_chat.services.faststream import fast_stream_router
from live_chat.web.api.messages.schema import ChatMessage
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
            channel = f"{data["type"]}: {data["recipient_id"]}"
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
    sender_ws = websocket_manager.active_connections[message.sender_id]
    recipient_id = message.recipient_id
    if recipient_id == message.sender_id:
        await sender_ws.send_text("Вы не можете отправить сообщение себе")
    elif recipient_id in websocket_manager.active_connections:
        await websocket_manager.send_personal_message(message.message, recipient_id)
    else:
        await sender_ws.send_text("Пользователь не найден")


# TODO: временно не работает (нужно добавить подключение к группе)
@fast_stream_router.subscriber(channel="group:{group_id}")
async def receive_message_from_group(
    message: ChatMessage,
    group_id: str,
) -> None:
    """Обрабатываем сообщения и отправляем их группе."""
    sender_ws = websocket_manager.active_connections[group_id]
    recipient_id = message.recipient_id
    if message.type == "group":
        await websocket_manager.send_group_message(message.message, recipient_id)
    else:
        await sender_ws.send_text("Неверный тип сообщения")
