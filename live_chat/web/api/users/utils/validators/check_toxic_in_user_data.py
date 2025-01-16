from typing import Dict

from fastapi import FastAPI

from live_chat.db.models.chat import User  # type: ignore[attr-defined]
from live_chat.web.ai_tools import ToxicEng, ToxicRus
from live_chat.web.api.users.utils.create_warning import create_warning_for_user


async def toxicity_determination(
    toxicity_scores: Dict[str, dict[str, str | float]],
    user: User,
    warning: bool = False,
) -> bool:
    """Function for determining toxicity in user data."""
    for field, score in toxicity_scores.items():
        toxicity = str(score.get("toxicity"))
        score_value = score.get("score")

        if score_value is not None:
            try:
                score_value = float(score_value)
            except ValueError:
                continue

            if toxicity == "toxic" and score_value > 0.7:
                warning = True
                await create_warning_for_user(field=field, user=user)
    return warning


async def check_user_data_for_toxic(user: User, app: FastAPI) -> None:
    """Function to check user data for toxicity."""
    # TODO добавить проверку аватарки пользователя
    toxic_rus: ToxicRus = app.state.toxic_rus
    toxic_eng: ToxicEng = app.state.toxic_eng
    toxicity_scores = {
        "first_name": toxic_rus.get_toxicity(user.first_name),
        "last_name": toxic_rus.get_toxicity(user.last_name),
        "username": toxic_eng.get_toxicity(user.username),
    }
    await toxicity_determination(toxicity_scores=toxicity_scores, user=user)
