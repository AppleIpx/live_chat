from typing import Any, Dict

from sqladmin import ModelView
from sqladmin.forms import Form
from starlette.requests import Request
from wtforms import BooleanField, FileField
from wtforms.fields.simple import PasswordField, StringField
from wtforms.validators import DataRequired, Email

from live_chat.db.models.chat import User  # type: ignore[attr-defined]
from live_chat.web.admin.utils.transformation import transformation_new_user_admin


class UserForm(Form):
    """Custom form for user model with definition specific fields."""

    username = StringField("Username", validators=[DataRequired()])
    first_name = StringField("First Name", default="")
    last_name = StringField("Last Name", default="")
    email = StringField("Email", validators=[Email()])
    hashed_password = PasswordField("Password", validators=[DataRequired()])
    user_image = FileField("User Image")
    is_active = BooleanField("Is Active", default=True)
    is_deleted = BooleanField("Is Deleted", default=False)
    is_verified = BooleanField("Is Verified", default=False)


class UserAdmin(ModelView, model=User):
    """User class that appears in the admin panel."""

    column_list = (
        User.id,
        User.username,
        User.first_name,
        User.last_name,
        User.last_online,
        User.is_superuser,
    )
    column_details_list = (
        *column_list,
        User.email,
        User.user_image,
        User.hashed_password,
        User.created_at,
        User.is_active,
        User.is_deleted,
        User.is_verified,
    )
    form = UserForm
    column_searchable_list = (User.username, User.email)
    column_sortable_list = (User.username, User.is_superuser)
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"
    category = "accounts"
    page_size = 50
    page_size_options = (25, 50, 100, 200)

    async def insert_model(self, request: Request, data: Dict[str, Any]) -> Any:
        """Function to add a new user through the admin panel."""
        data = await transformation_new_user_admin(data=data)
        return await super().insert_model(request, data)
