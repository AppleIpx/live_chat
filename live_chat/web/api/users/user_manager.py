import logging
import uuid
from typing import Any, Optional, Union

from fastapi import HTTPException
from fastapi_users import (
    BaseUserManager,
    UUIDIDMixin,
    exceptions,
    models,
    schemas,
)
from starlette import status
from starlette.requests import Request

from live_chat.db.models.user import User
from live_chat.services.faststream import fast_stream_broker
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

    async def on_after_register(
        self,
        user: models.UP,
        request: Optional[Request] = None,
    ) -> None:
        """
        Overridden method from the BaseUserManager.

        Performs a toxicity check user's data after registration.
        """
        if settings.use_ai:
            if request is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="The request was not sent",
                )
            await fast_stream_broker.publish(channel=f"{user.id!s}:check_toxic")

    async def _update(self, user: models.UP, update_dict: dict[str, Any]) -> User:
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

        return await super()._update(user, update_dict)  # type: ignore[arg-type]

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

    async def on_after_update(
        self,
        user: models.UP,
        update_dict: dict[str, Any],
        request: Optional[Request] = None,
    ) -> None:
        """Publish logs for admin when blocked user update account."""
        if user.is_banned and user.ban_reason:  # type: ignore[attr-defined]
            admin_message = (
                f"User {user.username} who was blocked due to "  # type: ignore[attr-defined]
                f"{user.ban_reason} updated account: \n{update_dict}"  # type: ignore[attr-defined]
            )
            logging.warning(admin_message)
        await fast_stream_broker.publish(channel=f"{user.id!s}:check_toxic")
