from sqladmin import ModelView

from live_chat.db.models.warnings import WarningLastName  # type: ignore[attr-defined]
from live_chat.web.admin.models.warnings.base_warning import BaseWarningAdmin


class WarningLastNameAdmin(BaseWarningAdmin, ModelView, model=WarningLastName):
    """WarningFirstName class that appears in the admin panel."""

    name = "Предупреждение фамилии"
    name_plural = "Предупреждения фамилий"
