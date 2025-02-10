from sqladmin import ModelView

from live_chat.db.models.chat import WarningLastName  # type: ignore[attr-defined]
from live_chat.web.admin.forms import WarningForm


class WarningLastNameAdmin(ModelView, model=WarningLastName):
    """WarningFirstName class that appears in the admin panel."""

    column_list = (
        WarningLastName.id,
        WarningLastName.correction_deadline,
    )
    column_details_list = (
        *column_list,
        "user",
        WarningLastName.created_at,
        WarningLastName.reason,
        WarningLastName.user_id,
        WarningLastName.ai_detection,
    )
    form = WarningForm

    can_edit = False
    can_delete = False
    name = "Предупреждение фамилии"
    name_plural = "Предупреждение фамилий"
    category = "Предупреждения"
    icon = "fa-solid fa-triangle-exclamation"
    page_size = 50
    page_size_options = (25, 50, 100, 200)
