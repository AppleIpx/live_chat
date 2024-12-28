import json

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.chat import (
    BlackList,
    Chat,
    DeletedMessage,
    Message,
    Reaction,
    User,
)
from tests.factories import MessageFactory

payload = {
    "email": "user1@example.com",
    "password": "string_123",
    "first_name": "string",
    "last_name": "string",
    "username": "username123!",
    "user_image": None,
    "is_deleted": False,
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
            },
        ),
    )
