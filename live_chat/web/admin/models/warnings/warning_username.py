from sqladmin import ModelView

from live_chat.db.models.warnings import WarningUsername  # type: ignore[attr-defined]
from live_chat.web.admin.models.warnings.base_warning import BaseWarningAdmin


class WarningUserNameAdmin(BaseWarningAdmin, ModelView, model=WarningUsername):
    """WarningFirstName class that appears in the admin panel."""

    name = "Предупреждение никнейма"
    name_plural = "Предупреждения никнеймов"
