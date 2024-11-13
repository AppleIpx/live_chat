import logging
from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi_users_db_sqlalchemy import UUID_ID
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.websockets import WebSocket

from live_chat.web.api.chat.schemas import (
    GetMessageSchema,
)
from live_chat.web.websocket.enums import WebSocketDisconnectTypes
from live_chat.web.websocket.mixins import UsageModelMixin
from live_chat.web.websocket.schemas import (
    ChatConnections,
    SendMessageWebSocketSchema,
    UserConnection,
)

logger = logging.getLogger(__name__)


class WebSocketManager(UsageModelMixin):
    """Websocket Maintenance Manager."""

    def __init__(self) -> None:
        self.active_connections: dict[UUID_ID, ChatConnections] = {}
        self.db_session: AsyncSession | None = None

    async def _send_error_message(
        self,
        username: str,
        chat_id: UUID_ID,
        error: dict[str, Any],
    ) -> None:
        """Send an error message to the user."""
        user = self.active_connections[chat_id].users.get(username)
        if user and user.is_online:
            await user.websocket.send_json(error)

    async def _send_message(
        self,
        chat_id: UUID_ID,
        message: SendMessageWebSocketSchema,
    ) -> None:
        if self.active_connections.get(chat_id):
            if created_message := await self.save_message_to_db(
                self.db_session,  # type: ignore[arg-type]
                message,
            ):
                message_data = GetMessageSchema(
                    message_id=created_message.id,
                    content=created_message.content,
                    created_at=created_message.created_at,
                    user_id=created_message.user_id,
                    chat_id=created_message.chat_id,
                )
                for username, connection in self.active_connections[
                    chat_id
                ].users.items():
                    if username != message.user.username and connection.is_online:
                        message_data = jsonable_encoder(message_data)
                        await connection.websocket.send_json(message_data)
            else:
                await self._send_error_message(
                    message.user.username,
                    chat_id,
                    {"error_type": "Message is not created in database."},
                )
        else:
            logger.warning("Chat does not exist.")

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
        disconnect_type: WebSocketDisconnectTypes,
    ) -> None:
        """Disconnects the user based on the specified disconnect type."""
        if (
            chat_id in self.active_connections
            and username in self.active_connections[chat_id].users
        ):
            if disconnect_type == WebSocketDisconnectTypes.DISCONNECT_WEBSOCKET:
                # Mark the user as offline in this chat, but keep WebSocket active
                self.active_connections[chat_id].users[username].is_online = False
            elif disconnect_type == WebSocketDisconnectTypes.LEAVE_CHAT:
                # Completely remove the user's WebSocket connection in chat
                del self.active_connections[chat_id].users[username]
                if not self.active_connections[chat_id].users:
                    del self.active_connections[chat_id]

    async def send_message(self, message: SendMessageWebSocketSchema) -> None:
        """Send a message in direct or group chat."""
        chat_id = message.chat.id
        if self.db_session:
            await self._send_message(chat_id, message)
        else:
            await self._send_error_message(
                message.user.username,
                chat_id,
                error={"error_type": "Database session is not initialized."},
            )
            logger.warning("Database session is not initialized.")


websocket_manager: WebSocketManager = WebSocketManager()
