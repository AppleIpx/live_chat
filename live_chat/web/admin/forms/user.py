from wtforms import FileField, Form, PasswordField, StringField
from wtforms.validators import DataRequired, Email


class UserForm(Form):
    """Custom form for user model with definition specific fields."""

    username = StringField("Username", validators=[DataRequired()])
    first_name = StringField("First Name", default="")
    last_name = StringField("Last Name", default="")
    email = StringField("Email", validators=[Email()])
    hashed_password = PasswordField("Password", validators=[DataRequired()])
    user_image = FileField("User Image")
