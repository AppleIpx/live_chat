from starlette.websockets import WebSocket


class WebSocketManager:
    """Websocket Maintenance Manager."""

    def __init__(self) -> None:
        self.active_connections: dict[str, WebSocket] = {}
        self.groups: dict[str, set[str]] = {}

    async def connect(self, websocket: WebSocket, user_id: str) -> None:
        """Establishing the connection."""
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str) -> None:
        """Disconnecting the user."""
        del self.active_connections[user_id]

    async def send_return_message(self, message: str, user_id: str) -> None:
        """Return the message to the recipient."""
        await self.active_connections[user_id].send_text(message)

    async def send_direct_message(self, message: str, user_id: str) -> None:
        """Send a private message to the user."""
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            await websocket.send_text(message)
        else:
            await self.send_return_message("Пользователь не подключен", user_id)

    async def send_group_message(self, message: str, group_id: str) -> None:
        """Send a message to all users in the group."""
        if group_id in self.groups:
            for user_id in self.groups[group_id]:
                await self.send_direct_message(message, user_id)

    async def add_to_group(self, user_id: str, group_id: str) -> bool:
        """Add the user to the group."""
        if group_id not in self.groups:
            self.groups[group_id] = set()
        if user_id in self.groups.get(group_id, set()):
            await self.send_return_message(
                f"Вы уже состоите в группе {group_id}.",
                user_id,
            )
            return False
        self.groups[group_id].add(user_id)
        return True

    async def remove_from_group(self, user_id: str, group_id: str) -> None:
        """Remove the user from the group."""
        if group_id in self.groups:
            self.groups[group_id].discard(user_id)


websocket_manager: WebSocketManager = WebSocketManager()
