from sqladmin import ModelView

from live_chat.db.models.chat import Task  # type: ignore[attr-defined]
from live_chat.web.admin.utils.identifier_utils import CustomStmtMixin


class TaskAdmin(CustomStmtMixin, ModelView, model=Task):
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
