from typing import Dict

from fastapi import FastAPI
from lingua import Language, LanguageDetectorBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.user import User
from live_chat.web.ai_tools import ToxicEng, ToxicRus
from live_chat.web.api.users.utils.create_warning import create_warning_for_user


async def toxicity_determination(
    toxicity_scores: Dict[str, dict[str, str | float]],
    user: User,
    db_session: AsyncSession,
    warning: bool = False,
) -> bool:
    """Function for determining toxicity in user data."""
    for field, score in toxicity_scores.items():
        toxicity = str(score.get("label"))
        score_value = score.get("score")

        if score_value is not None:
            try:
                score_value = float(score_value)
            except ValueError:
                continue
            if toxicity == "toxic" and score_value > 0.7:
                warning = True
                await create_warning_for_user(
                    field=field,
                    user=user,
                    db_session=db_session,
                )
    return warning


async def determination_language(text: str) -> str:
    """Function for determining language in user data."""
    languages = [Language.ENGLISH, Language.RUSSIAN]
    detector = LanguageDetectorBuilder.from_languages(*languages).build()
    return detector.detect_language_of(text).name  # type: ignore[union-attr]


async def check_user_data_for_toxic(
    user: User,
    app: FastAPI,
    db_session: AsyncSession,
) -> None:
    """Function to check user data for toxicity."""
    # TODO добавить проверку аватарки пользователя
    toxic_rus: ToxicRus = app.state.toxic_rus
    toxic_eng: ToxicEng = app.state.toxic_eng

    first_name_language = await determination_language(user.first_name)
    last_name_language = await determination_language(user.last_name)

    toxic_scores = {
        "first_name": (
            toxic_rus.get_toxicity(user.first_name)
            if first_name_language == "RUSSIAN"
            else toxic_eng.get_toxicity(user.first_name)
        ),
        "last_name": (
            toxic_rus.get_toxicity(user.last_name)
            if last_name_language == "RUSSIAN"
            else toxic_eng.get_toxicity(user.last_name)
        ),
        "username": toxic_eng.get_toxicity(user.username),
    }
    await toxicity_determination(
        toxicity_scores=toxic_scores,
        user=user,
        db_session=db_session,
    )
