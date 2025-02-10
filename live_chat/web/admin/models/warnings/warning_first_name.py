from sqladmin import ModelView

from live_chat.db.models.chat import WarningFirstName  # type: ignore[attr-defined]
from live_chat.web.admin.models.warnings.base_warning import BaseWarningAdmin


class WarningFirstNameAdmin(BaseWarningAdmin, ModelView, model=WarningFirstName):
    """WarningFirstName class that appears in the admin panel."""

    name = "Предупреждение имени"
    name_plural = "Предупреждения имен"
