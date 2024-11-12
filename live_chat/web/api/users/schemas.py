import uuid

from fastapi_users import BaseUserManager, UUIDIDMixin, schemas
from fastapi_users_db_sqlalchemy import UUID_ID

from live_chat.db.models.chat import User  # type: ignore[attr-defined]
from live_chat.settings import settings


class BaseUserSchema:
    """Base user schemas."""

    first_name: str
    last_name: str
    username: str


class UserRead(BaseUserSchema, schemas.BaseUser[UUID_ID]):
    """Represents a read command for a user."""


class UserCreate(BaseUserSchema, schemas.BaseUserCreate):
    """Represents a create command for a user."""


class UserUpdate(schemas.BaseUserUpdate):
    """Represents an update command for a user."""


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    """Manages a user session and its tokens."""

    reset_password_token_secret = settings.users_secret
    verification_token_secret = settings.users_secret
