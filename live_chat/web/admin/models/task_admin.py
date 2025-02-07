from typing import Any

from sqladmin import ModelView
from sqladmin.helpers import get_primary_keys
from sqlalchemy import Select, select
from starlette.requests import Request

from live_chat.db.models.chat import Task  # type: ignore[attr-defined]
from live_chat.web.admin.utils import CustomQuery, custom_object_identifier_values


class TaskAdmin(ModelView, model=Task):
    """User class that appears in the admin panel."""

    column_list = (
        Task.id,
        Task.user,
        Task.type,
        Task.status,
        Task.updated_at,
        Task.finished_at,
    )
    column_details_list = (
        *column_list,
        Task.chat_id,
        Task.created_at,
    )
    column_searchable_list = (Task.user, Task.type)
    column_sortable_list = (
        Task.status,
        Task.updated_at,
        Task.finished_at,
    )
    can_edit = False
    can_delete = False
    can_create = False
    name = "Задача"
    name_plural = "Задачи"
    icon = "fa-solid fa-bars-progress"
    page_size = 50
    page_size_options = (25, 50, 100, 200)

    async def delete_model(self, request: Request, pk: Any) -> None:
        """Function to mark user is_deleted flag through the admin panel."""
        await CustomQuery(self).delete(pk, request)

    def _stmt_by_identifier(self, identifier: str) -> Select[Any]:
        stmt: Select[Any] = select(self.model)
        pks = get_primary_keys(self.model)
        values = custom_object_identifier_values(identifier, self.model)
        conditions = [pk == value for (pk, value) in zip(pks, values)]
        return stmt.where(*conditions)
