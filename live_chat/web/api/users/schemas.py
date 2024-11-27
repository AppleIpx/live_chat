from typing import List, Optional

from fastapi_users import schemas
from fastapi_users_db_sqlalchemy import UUID_ID
from pydantic import BaseModel, HttpUrl


class BaseUserSchema:
    """Base user schema."""

    first_name: str
    last_name: str
    username: str
    user_image: HttpUrl | None


class BaseUserUpdateSchema:
    """Base user schema for update."""

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None


class UserRead(BaseUserSchema, schemas.BaseUser[UUID_ID]):
    """Represents a read command for a user."""


class ListUserSchema(BaseModel):
    """Represents a list command for a user."""

    users: List[UserRead]


class UserCreate(BaseUserSchema, schemas.BaseUserCreate):
    """Represents a create command for a user."""


class UserUpdate(BaseUserUpdateSchema, schemas.BaseUserUpdate):
    """Represents an update command for a user."""
