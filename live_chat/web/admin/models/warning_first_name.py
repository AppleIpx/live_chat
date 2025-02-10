from sqladmin import ModelView

from live_chat.db.models.warnings import WarningFirstName
from live_chat.web.admin.forms import WarningForm


class WarningFirstNameAdmin(ModelView, model=WarningFirstName):
    """WarningFirstName class that appears in the admin panel."""

    column_list = (
        WarningFirstName.id,
        WarningFirstName.correction_deadline,
    )
    column_details_list = (  # type: ignore[assignment]
        *column_list,
        "user",
        WarningFirstName.created_at,
        WarningFirstName.reason,
        WarningFirstName.user_id,
        WarningFirstName.ai_detection,
    )
    form = WarningForm

    can_edit = False
    can_delete = False
    name = "Предупреждение имени"
    name_plural = "Предупреждение имен"
    # icon =
    page_size = 50
    page_size_options = (25, 50, 100, 200)
