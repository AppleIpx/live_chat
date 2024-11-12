import logging

from fastapi_users_db_sqlalchemy import UUID_ID
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.websockets import WebSocket

from live_chat.web.websocket.enums import DisconnectType
from live_chat.web.websocket.messages.schemas import SendMessageWebSocketSchema
from live_chat.web.websocket.schemas import ChatConnections, UserConnection
from live_chat.web.websocket.utils import get_chat_by_id


class WebSocketManager:
    """Websocket Maintenance Manager."""

    def __init__(self) -> None:
        self.active_connections: dict[UUID_ID, ChatConnections] = {}
        self.db_session: AsyncSession | None = None

    async def _send_message(
        self,
        chat_id: UUID_ID,
        message: SendMessageWebSocketSchema,
    ) -> None:
        if self.active_connections.get(chat_id):
            for username, connection in self.active_connections[chat_id].users.items():
                if username != message.user.username and connection.is_online:
                    await connection.websocket.send_text(message.content)
        else:
            logging.warning("Chat does not exist.")

    async def send_error_message(
        self,
        username: str,
        chat_id: UUID_ID,
        message: str,
    ) -> None:
        """Send an error message to the user."""
        user = self.active_connections[chat_id].users.get(username)
        if user and user.is_online:
            await user.websocket.send_text(message)

    async def connect(
        self,
        websocket: WebSocket,
        username: str,
        chat_id: UUID_ID,
    ) -> None:
        """Start the connection."""
        await websocket.accept()
        if chat_id not in self.active_connections:
            self.active_connections[chat_id] = ChatConnections(chat_id=chat_id)
        self.active_connections[chat_id].users[username] = UserConnection(
            websocket=websocket,
        )

    async def disconnect(
        self,
        username: str,
        chat_id: UUID_ID,
        disconnect_type: DisconnectType,
    ) -> None:
        """Disconnects the user based on the specified disconnect type."""
        if (
            chat_id in self.active_connections
            and username in self.active_connections[chat_id].users
        ):
            if disconnect_type == DisconnectType.DISCONNECT_WEBSOCKET:
                # Mark the user as offline in this chat, but keep WebSocket active
                self.active_connections[chat_id].users[username].is_online = False
            elif disconnect_type == DisconnectType.LEAVE_CHAT:
                # Completely remove the user's WebSocket connection in chat
                del self.active_connections[chat_id].users[username]
                if not self.active_connections[chat_id].users:
                    del self.active_connections[chat_id]

    async def send_message(self, message: SendMessageWebSocketSchema) -> None:
        """Send a private message to the user."""
        if self.db_session:
            if chat := await get_chat_by_id(
                self.db_session,
                chat_id=message.chat.id,
            ):
                await self._send_message(chat.id, message)
            else:
                logging.warning("The chat is not in the database.")
        else:
            logging.warning("Database session is not initialized.")

    """
    Moved to API

    async def add_to_group(self, username: str, group_id: str) -> bool:
        "Add the user to the group."
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
        "Remove the user from the group."
        if group_id in self.groups:
            self.groups[group_id].discard(username)
    """


websocket_manager: WebSocketManager = WebSocketManager()
