from starlette.websockets import WebSocket


class WebSocketManager:
    """Менеджер для вебсокетов."""

    def __init__(self) -> None:
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str) -> None:
        """Устанавливаем соединение."""
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str) -> None:
        """Отключаем пользователя."""
        del self.active_connections[user_id]

    async def send_personal_message(self, message: str, user_id: str) -> None:
        """Отправляем личное сообщение пользователю."""
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            await websocket.send_text(message)
        else:
            await self.active_connections[user_id].send_text("message")

    async def send_group_message(self, message: str, group_id: str) -> None:
        """Отправляем сообщение всем пользователям в группе."""
        for user_id, websocket in self.active_connections.items():
            if user_id.startswith(group_id):
                await websocket.send_text(message)
