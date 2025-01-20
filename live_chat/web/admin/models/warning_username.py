from sqladmin import ModelView

from live_chat.db.models.chat import WarningUsername  # type: ignore[attr-defined]
from live_chat.web.admin.forms import WarningForm


class WarningUserNameAdmin(ModelView, model=WarningUsername):
    """WarningFirstName class that appears in the admin panel."""

    column_list = (
        WarningUsername.id,
        WarningUsername.correction_deadline,
    )
    column_details_list = (
        *column_list,
        "user",
        WarningUsername.created_at,
        WarningUsername.reason,
        WarningUsername.user_id,
        WarningUsername.ai_detection,
    )
    form = WarningForm

    can_edit = False
    can_delete = False
    name = "Предупреждение никнейма"
    name_plural = "Предупреждение никнейма"
    # icon =
    page_size = 50
    page_size_options = (25, 50, 100, 200)
