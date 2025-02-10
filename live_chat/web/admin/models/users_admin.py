from typing import Any, Dict
from uuid import UUID

from fastapi import HTTPException
from sqladmin import ModelView, action
from sqladmin.helpers import (
    get_primary_keys,
)
from sqlalchemy import Select, select
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from live_chat.db.models.user import User
from live_chat.db.utils import async_session_maker
from live_chat.web.admin.forms import UserForm
from live_chat.web.admin.utils import CustomQuery, custom_object_identifier_values
from live_chat.web.admin.utils.transformation import transformation_new_user_admin
from live_chat.web.api.users.utils import get_user_by_id


class UserAdmin(ModelView, model=User):
    """User class that appears in the admin panel."""

    column_list = (  # type: ignore[assignment]
        User.id,
        User.username,
        User.first_name,
        User.last_name,
        User.email,
        User.is_superuser,
        User.is_deleted,
        User.is_banned,
    )
    column_details_list = (
        *column_list,  # type: ignore[has-type]
        User.user_image,
        User.created_at,
        User.last_online,
        User.is_active,  # type: ignore[arg-type]
        User.is_verified,  # type: ignore[arg-type]
        User.ban_reason,
    )
    form = UserForm
    details_template = "user_details.html"
    column_searchable_list = (User.username, User.email)
    column_sortable_list = (  # type: ignore[assignment]
        User.username,
        User.is_superuser,
        User.is_deleted,
        User.is_banned,
    )
    can_edit = False
    name = "Пользователь"
    name_plural = "Пользователи"
    icon = "fa-solid fa-user"
    page_size = 50
    page_size_options = (25, 50, 100, 200)

    async def insert_model(self, request: Request, data: Dict[str, Any]) -> Any:
        """Function to add a new user through the admin panel."""
        data = await transformation_new_user_admin(data=data)
        return await super().insert_model(request, data)

    async def delete_model(self, request: Request, pk: Any) -> None:
        """Function to mark user is_deleted flag through the admin panel."""
        await CustomQuery(self).delete(pk, request)

    def _stmt_by_identifier(self, identifier: str) -> Select[Any]:
        stmt: Select[Any] = select(self.model)
        pks = get_primary_keys(self.model)
        values = custom_object_identifier_values(identifier, self.model)
        conditions = [pk == value for (pk, value) in zip(pks, values)]
        return stmt.where(*conditions)

    @action(
        name="toggle_ban",
        label=None,
        confirmation_message=None,
        add_in_detail=False,
        add_in_list=False,
    )
    async def toggle_ban(self, request: Request) -> JSONResponse:
        """Manages the blocking or unblocking of the user."""
        if user_id := request.query_params.get("pk"):
            reason = request.query_params.get("reason", None)
            async with async_session_maker() as session:
                user: User | None = await get_user_by_id(
                    db_session=session,
                    user_id=UUID(user_id),
                )
                user.is_banned = not user.is_banned  # type: ignore[union-attr]
                user.ban_reason = reason if user.is_banned else None  # type: ignore[union-attr]
                session.add(user)
                await session.commit()
            return JSONResponse(status_code=status.HTTP_200_OK, content=None)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No primary key provided",
        )
