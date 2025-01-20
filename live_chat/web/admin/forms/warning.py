from sqladmin.fields import DateTimeField
from wtforms import BooleanField, Form, StringField
from wtforms.validators import DataRequired, Length, Optional


class WarningForm(Form):
    """Custom form for user model with definition specific fields."""

    reason = StringField(
        "Reason",
        validators=[DataRequired(), Length(max=500)],
        description="Reason for the warning (max 500 characters).",
    )
    ai_detection = BooleanField(
        "AI Detection",
        default=False,
        description="Was this warning generated by AI?",
    )
    correction_deadline = DateTimeField(
        "Correction Deadline",
        format="%Y-%m-%d %H:%M:%S",
        validators=[Optional()],
        description="Deadline for correcting the issue (optional).",
    )
    user_id = StringField(
        "User ID",
        validators=[DataRequired()],
        description="ID of the user associated with the warning.",
    )
