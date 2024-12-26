from typing import Any, Dict

from live_chat.web.api.users.utils.validators import validate_password


async def start_all_validators(data: Dict[str, Any]) -> bool:
    """A function that runs all the necessary validators."""
    # TODO внести все возможные проверки (имя пользователя, почты и тд)
    password_validator = await validate_password(
        email=data["email"],
        username=data["username"],
        password=data["hashed_password"],
    )
    return bool(password_validator)
