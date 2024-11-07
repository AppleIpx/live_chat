import logging

from fastapi import APIRouter
from starlette.websockets import WebSocket, WebSocketDisconnect

from live_chat.services.faststream import fast_stream_router
from live_chat.web.api.messages.schema import DirectMessage

router = APIRouter()
logger = logging.getLogger(__name__)
active_clients: dict[str, WebSocket] = {}


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str) -> None:
    """Подключение WebSocket."""
    await websocket.accept()
    active_clients[user_id] = websocket
    try:
        while True:
            data = await websocket.receive_json()
            await fast_stream_router.broker.publish(
                data,
                user_id,
            )
    except WebSocketDisconnect:
        logger.info(f"Client {user_id} disconnected")
    finally:
        del active_clients[user_id]


@fast_stream_router.subscriber(channel="{user_id}")
async def receive_message_from_user(message: DirectMessage, user_id: str) -> None:
    """Отправка сообщения пользователю."""
    sender_ws = active_clients[user_id]
    recipient_id = message.recipient_id
    if recipient_id == user_id:
        await sender_ws.send_text("Вы не можете отправить сообщение себе")
    elif recipient_id in active_clients:
        client_ws = active_clients[recipient_id]
        await client_ws.send_text(message.message)
    else:
        await sender_ws.send_text("Пользователь не найден")
