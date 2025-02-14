from datetime import datetime, timedelta, timezone
from typing import Type, Union

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.user import User
from live_chat.db.models.warnings import (
    WarningFirstName,
    WarningLastName,
    WarningUsername,
)
from live_chat.db.utils import async_session_maker

WARNING_MODELS_MAP = {
    "first_name": WarningFirstName,
    "last_name": WarningLastName,
    "username": WarningUsername,
}


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


async def create_warning_for_user(field: str, user: User) -> None:
    """Function that creates warnings for the user."""
    async with async_session_maker() as db_session:
        if not user.is_warning:
            user.is_warning = True
            db_session.add(user)
            await db_session.commit()

        warning_model = WARNING_MODELS_MAP.get(field)
        if warning_model:
            await create_warning(
                field=field,
                db_session=db_session,
                user=user,
                warning_model=warning_model,  # type: ignore[arg-type]
            )


async def delete_warnings_for_user(user: User) -> None:
    """Function that delete warnings for the user."""
    async with async_session_maker() as db_session:
        if user.is_warning:
            user.is_warning = False
            db_session.add(user)
            for model in WARNING_MODELS_MAP.values():
                query = delete(model).where(model.user_id == user.id)
                await db_session.execute(query)
                await db_session.commit()
