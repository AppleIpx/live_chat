from sqladmin import ModelView

from live_chat.db.models.chat import User  # type: ignore[attr-defined]


class UserAdmin(ModelView, model=User):
    """User class that appears in the admin panel."""

    column_list = (
        User.id,
        User.username,
        User.first_name,
        User.last_name,
        User.last_online,
    )
    column_searchable_list = (User.username, User.last_name)
    column_sortable_list = (User.username, User.last_online)
    can_create = True
    can_edit = True
    can_delete = False
    can_view_details = True
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"
    category = "accounts"
    page_size = 50
    page_size_options = (25, 50, 100, 200)
