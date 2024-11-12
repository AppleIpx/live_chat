from sqlalchemy.ext.asyncio import AsyncSession
from starlette.websockets import WebSocket

from live_chat.web.websocket.mixins import SelectUserMixin


class WebSocketManager(SelectUserMixin):
    """Websocket Maintenance Manager."""

    def __init__(self) -> None:
        self.active_connections: dict[str, WebSocket] = {}
        self.groups: dict[str, set[str]] = {}
        self.db_session: AsyncSession | None = None

    async def connect(self, websocket: WebSocket, username: str) -> None:
        """Start the connection."""
        await websocket.accept()
        self.active_connections[username] = websocket

    def disconnect(self, username: str) -> None:
        """Disconnecting the user."""
        del self.active_connections[username]

    async def send_return_message(self, message: str, username: str) -> None:
        """Return the message to the recipient."""
        await self.active_connections[username].send_text(message)

    async def send_direct_message(self, message: str, username: str) -> None:
        """Send a private message to the user."""
        if self.db_session and (
            user := await self.get_user_by_username(self.db_session, username=username)
        ):
            websocket = self.active_connections[user.username]
            await websocket.send_text(message)

    async def send_group_message(self, message: str, group_id: str) -> None:
        """Send a message to all users in the group."""
        if group_id in self.groups:
            for username in self.groups[group_id]:
                await self.send_direct_message(message, username)

    async def add_to_group(self, username: str, group_id: str) -> bool:
        """Add the user to the group."""
        if group_id not in self.groups:
            self.groups[group_id] = set()
        if username in self.groups.get(group_id, set()):
            await self.send_return_message(
                f"Вы уже состоите в группе {group_id}.",
                username,
            )
            return False
        self.groups[group_id].add(username)
        return True

    async def remove_from_group(self, username: str, group_id: str) -> None:
        """Remove the user from the group."""
        if group_id in self.groups:
            self.groups[group_id].discard(username)


websocket_manager: WebSocketManager = WebSocketManager()
