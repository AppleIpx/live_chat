from datetime import datetime, timedelta, timezone
from typing import Type, Union

from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.chat import (  # type: ignore[attr-defined]
    User,
    WarningFirstName,
    WarningLastName,
    WarningUsername,
)


async def get_reason(field: str) -> str:
    """A function that returns the reason for the warning."""
    return (
        f"Your {field} has not been tested for toxicity. Reasons may include using "
        f"inappropriate words, racist or discriminatory language, sexual "
        f"innuendo, violating community rules, or attempting to fake an identity. "
        f"Please choose a different {field} that meets our community standards."
    )


async def create_warning(
    db_session: AsyncSession,
    field: str,
    user: User,
    warning_model: Type[Union[WarningFirstName, WarningLastName, WarningUsername]],
) -> None:
    """A function that creates a warning."""
    warning = warning_model(
        reason=await get_reason(field),
        ai_detection=True,
        user_id=user.id,
        correction_deadline=datetime.now(timezone.utc) + timedelta(days=7),
        user=user,
    )
    db_session.add(warning)
    await db_session.commit()


async def create_warning_for_user(
    field: str,
    user: User,
    db_session: AsyncSession,
) -> None:
    """Function that creates warnings for the user."""
    if not user.is_warning:
        user.is_warning = True
        db_session.add(user)
        await db_session.commit()

    warnings_models = {
        "first_name": WarningFirstName,
        "last_name": WarningLastName,
        "username": WarningUsername,
    }
    warning_model = warnings_models.get(field)
    if warning_model:
        await create_warning(
            field=field,
            db_session=db_session,
            user=user,
            warning_model=warning_model,
        )
