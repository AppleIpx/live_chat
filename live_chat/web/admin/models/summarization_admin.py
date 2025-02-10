from sqladmin import ModelView

from live_chat.db.models.chat import Summarization  # type: ignore[attr-defined]
from live_chat.web.admin.utils.identifier_utils import CustomStmtMixin


class SummarizationAdmin(CustomStmtMixin, ModelView, model=Summarization):
    """Summarization class that appears in the admin panel."""

    column_list = (
        Summarization.id,
        Summarization.user,
        Summarization.progress,
        Summarization.status,
        Summarization.updated_at,
        Summarization.finished_at,
    )
    column_details_list = (
        *column_list,
        Summarization.chat_id,
        Summarization.created_at,
    )
    column_searchable_list = (Summarization.user, Summarization.chat)
    column_sortable_list = (
        Summarization.status,
        Summarization.updated_at,
        Summarization.finished_at,
    )
    can_edit = False
    can_delete = False
    can_create = False
    name = "Задача"
    name_plural = "Задачи"
    icon = "fa-solid fa-bars-progress"
    page_size = 50
    page_size_options = (25, 50, 100, 200)
