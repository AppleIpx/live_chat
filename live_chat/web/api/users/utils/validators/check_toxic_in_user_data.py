import logging
from typing import Any, Dict
from uuid import UUID

from lingua import Language, LanguageDetectorBuilder

from live_chat.db.models.user import User
from live_chat.db.utils import async_session_maker
from live_chat.services.faststream import fast_stream_broker
from live_chat.web.ai_tools import ToxicEng, ToxicRus
from live_chat.web.api.users.utils.get_user import get_user_by_id
from live_chat.web.api.users.utils.usage_warning import (
    create_warning_for_user,
    delete_warnings_for_user,
)


async def toxicity_determination(
    toxicity_scores: Dict[str, dict[str, str | float]],
    user: User,
    warning: bool = False,
) -> None:
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
                await create_warning_for_user(field=field, user=user)
    if not warning:
        await delete_warnings_for_user(user=user)


async def determination_language(text: str) -> str:
    """Function for determining language in user data."""
    languages = [Language.ENGLISH, Language.RUSSIAN]
    detector = LanguageDetectorBuilder.from_languages(*languages).build()
    return detector.detect_language_of(text).name  # type: ignore[union-attr]


@fast_stream_broker.subscriber("{user_id}:check_toxic")
async def check_user_data_for_toxic(message: Any) -> None:
    """Function to check user data for toxicity."""
    # TODO добавить проверку аватарки пользователя
    user_id = message.path["user_id"]
    async with async_session_maker() as db_session:
        user = await get_user_by_id(db_session, user_id=UUID(user_id))
        if not user:
            error_message = f"User {user_id} was not found in db"
            logging.error(error_message)
            return
    toxic_rus, toxic_eng = ToxicRus(), ToxicEng()
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
    await toxicity_determination(toxicity_scores=toxic_scores, user=user)
