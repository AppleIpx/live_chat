from typing import ClassVar, Sequence, Union

from sqladmin._types import MODEL_ATTR
from wtforms.form import Form

from live_chat.web.admin.forms import WarningForm
from live_chat.web.admin.utils.identifier_utils import CustomStmtMixin


class BaseWarningAdmin(CustomStmtMixin):
    """Base class for warnings that appears in the admin panel."""

    column_list: ClassVar[Union[str, Sequence[MODEL_ATTR]]] = [
        "id",
        "correction_deadline",
        "ai_detection",
        "created_at",
    ]
    column_details_list: ClassVar[Union[str, Sequence[MODEL_ATTR]]] = [
        *column_list,
        "user",
        "reason",
        "user_id",
    ]
    form: ClassVar[Form] = WarningForm
    can_edit: ClassVar[bool] = False
    can_delete: ClassVar[bool] = False
    category: ClassVar[str] = "Предупреждения"
    icon: ClassVar[str] = "fa-solid fa-triangle-exclamation"
    page_size: ClassVar[int] = 50
    page_size_options: ClassVar[Sequence[int]] = [25, 50, 100, 200]
