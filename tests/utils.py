import json

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.black_list import BlackList
from live_chat.db.models.chat import (
    Chat,
)
from live_chat.db.models.messages import DeletedMessage, Message
from live_chat.db.models.reaction import Reaction
from live_chat.db.models.user import User
from tests.factories import MessageFactory

payload = {
    "email": "user1@example.com",
    "password": "string_123",
    "first_name": "string",
    "last_name": "string",
    "username": "username123!",
    "user_image": None,
    "is_deleted": False,
    "is_banned": False,
    "is_warning": False,
}

new_payload = {
    "email": "new_user@example.com",
    "password": "new_string_123",
    "first_name": "new_string",
    "last_name": "new_string",
    "username": "new_string",
    "user_image": None,
}


async def get_first_chat_from_db(
    db_session: AsyncSession,
) -> Chat | None:
    """Helper function for getting first chat from DB."""
    query = select(Chat)
    result = await db_session.execute(query)
    return result.scalars().first()


async def get_first_user_from_db(
    db_session: AsyncSession,
) -> User | None:
    """Helper function that returns the user who submitted the request."""
    query = select(User)
    result = await db_session.execute(query)
    return result.scalars().first()


async def get_first_deleted_message(db_session: AsyncSession) -> DeletedMessage | None:
    """Helper function that returns the deleted message."""
    query = select(DeletedMessage)
    result = await db_session.execute(query)
    return result.scalars().first()


async def get_first_black_list_from_db(db_session: AsyncSession) -> BlackList | None:
    """Helper function that returns the black list."""
    query = select(BlackList)
    result = await db_session.execute(query)
    return result.scalars().first()


async def get_first_reaction_from_db(db_session: AsyncSession) -> BlackList | None:
    """Helper function that returns the reaction."""
    query = select(Reaction)
    result = await db_session.execute(query)
    return result.scalars().first()


async def transformation_message_data(message: MessageFactory | Message) -> str:
    """Helper function that returns jsonable message_data for faststream."""
    return json.dumps(
        jsonable_encoder(
            {
                "id": message.id,
                "user_id": message.user.id,
                "chat_id": message.chat.id,
                "message_type": message.message_type,
                "file_name": message.file_name,
                "file_path": message.file_path,
                "content": message.content,
                "created_at": message.created_at,
                "updated_at": message.updated_at,
                "is_deleted": message.is_deleted,
                "reactions": [],
                "forwarded_message": message.forwarded_message,
                "parent_message": None,
            },
        ),
    )


async def transformation_forward_message_data(message: MessageFactory | Message) -> str:
    """Helper function that returns jsonable forwards message_data for faststream."""
    forwarded_message = jsonable_encoder(
        {
            "id": message.forwarded_message.id,
            "user": {
                "first_name": message.forwarded_message.user.first_name,
                "last_name": message.forwarded_message.user.last_name,
                "username": message.forwarded_message.user.username,
                "user_image": message.forwarded_message.user.user_image,
                "last_online": message.forwarded_message.user.last_online,
                "is_deleted": message.forwarded_message.user.is_deleted,
                "is_banned": message.forwarded_message.user.is_banned,
                "id": message.forwarded_message.user.id,
            },
        },
    )

    return json.dumps(
        jsonable_encoder(
            [
                {
                    "id": message.id,
                    "user_id": message.user.id,
                    "chat_id": message.chat.id,
                    "message_type": message.message_type,
                    "file_name": message.file_name,
                    "file_path": message.file_path,
                    "content": message.content,
                    "created_at": message.created_at.isoformat().replace("+00:00", "Z"),
                    "updated_at": message.updated_at.isoformat().replace("+00:00", "Z"),
                    "is_deleted": message.is_deleted,
                    "reactions": [],
                    "forwarded_message": forwarded_message,
                    "parent_message": None,
                },
            ],
        ),
    )
