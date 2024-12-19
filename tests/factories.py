import uuid
from datetime import datetime

import factory
from factory.fuzzy import FuzzyChoice

from live_chat.db.models.chat import Chat, DeletedMessage, Message, ReadStatus, User
from live_chat.db.models.enums import ChatType, MessageType


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    """A factory for creating instances of the User model for testing purposes."""

    class Meta:
        model = User
        sqlalchemy_session = None

    id = factory.LazyFunction(uuid.uuid4)
    username = factory.Faker("user_name")
    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    hashed_password = factory.Faker("password")
    last_name = factory.Faker("last_name")
    last_online = factory.LazyFunction(datetime.now)
    user_image = factory.Faker("image_url")
    is_active = factory.Faker("boolean")
    is_superuser = factory.Faker("boolean")
    is_verified = factory.Faker("boolean")
    created_at = factory.LazyFunction(datetime.now)
    updated_at = factory.LazyFunction(datetime.now)


class ChatFactory(factory.alchemy.SQLAlchemyModelFactory):
    """A factory for creating instances of the Chat model for testing purposes."""

    class Meta:
        model = Chat
        sqlalchemy_session = None

    id = factory.LazyFunction(uuid.uuid4)
    chat_type = factory.Faker("random_element", elements=list(ChatType))
    name = factory.Faker("name")
    image = factory.Faker("image_url")
    last_message_content = factory.Faker("text", max_nb_chars=100)
    created_at = factory.LazyFunction(datetime.now)
    updated_at = factory.LazyFunction(datetime.now)


class MessageFactory(factory.alchemy.SQLAlchemyModelFactory):
    """A factory for creating instances of the Message model for testing purposes."""

    class Meta:
        model = Message
        sqlalchemy_session = None

    id = factory.LazyFunction(uuid.uuid4)
    message_type = FuzzyChoice(MessageType)
    content = factory.Faker("text", max_nb_chars=5000)
    file_name = factory.Faker("text", max_nb_chars=50)
    file_path = factory.Faker("url")
    user = factory.SubFactory(UserFactory)
    chat = factory.SubFactory(ChatFactory)
    created_at = factory.LazyFunction(datetime.now)
    updated_at = factory.LazyFunction(datetime.now)
    is_deleted = factory.Faker("boolean")


class DeletedMessageFactory(MessageFactory):
    """A factory for creating the Deleted Message model for testing purposes."""

    class Meta:
        model = DeletedMessage
        sqlalchemy_session = None

    is_deleted = True


class ReadStatusFactory(factory.alchemy.SQLAlchemyModelFactory):
    """A factory for creating instances of the ReadStatus model for testing purposes."""

    class Meta:
        model = ReadStatus
        sqlalchemy_session = None

    id = factory.LazyFunction(uuid.uuid4)
    last_read_message_id = None
    count_unread_msg = factory.Faker("random_int", min=0, max=100)
    user = factory.SubFactory(UserFactory)
    chat = factory.SubFactory(ChatFactory)
    created_at = factory.LazyFunction(datetime.now)
    updated_at = factory.LazyFunction(datetime.now)
    is_deleted = factory.Faker("boolean")
