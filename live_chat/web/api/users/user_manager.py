import uuid
from typing import Any, Union

from fastapi import HTTPException
from fastapi_users import (
    BaseUserManager,
    UUIDIDMixin,
    exceptions,
    models,
    schemas,
)
from starlette import status

from live_chat.db.models.chat import User  # type: ignore[attr-defined]
from live_chat.settings import settings
from live_chat.web.api.users.utils.custom_user_db import CustomSQLAlchemyUserDatabase
from live_chat.web.api.users.utils.validators.password import validate_password


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    """Manages a user session and its tokens."""

    reset_password_token_secret = settings.users_secret
    verification_token_secret = settings.users_secret
    user_db = CustomSQLAlchemyUserDatabase  # type: ignore[assignment]

    async def get_by_username(self, username: str) -> models.UP:
        """
        Get a user by e-mail.

        :param username: username of the user to retrieve.
        :raises UserNotExists: The user does not exist.
        :return: A user.
        """
        user = await self.user_db.get_by_username(username)  # type: ignore[has-type]

        if user is None:
            raise exceptions.UserNotExists

        return user

    async def _update(self, user: models.UP, update_dict: dict[str, Any]) -> models.UP:
        for field, value in update_dict.items():
            if field == "username" and value != user.username:  # type: ignore[attr-defined]
                try:
                    await self.get_by_username(value)
                    raise exceptions.UserAlreadyExists
                except exceptions.UserNotExists:
                    pass
                except exceptions.UserAlreadyExists as error:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="UPDATE_USERNAME_ALREADY_EXISTS",
                    ) from error

        return await super()._update(user, update_dict)

    async def validate_password(
        self,
        password: str,
        user: Union[schemas.UC, models.UP],
    ) -> None:
        """Validate password."""
        await validate_password(
            email=user.email,
            username=user.username,  # type: ignore[union-attr]
            password=password,
        )
