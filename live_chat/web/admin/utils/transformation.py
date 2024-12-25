import datetime
from typing import Any, Dict

from live_chat.web.admin.utils.check_image_in_request import check_image
from live_chat.web.api.users.user_manager import UserManager
from live_chat.web.api.users.utils.dependency import get_user_db
from live_chat.web.api.users.utils.main_validator import start_all_validators


async def transformation_new_user_admin(data: Dict[str, Any]) -> Dict[str, Any]:
    """A function that fills in the necessary fields to create a user."""
    password = data["hashed_password"]
    image_url = await check_image(uploaded_image=data["user_image"])
    if await start_all_validators(data=data):
        user_manager = UserManager(user_db=get_user_db())
        data["hashed_password"] = user_manager.password_helper.hash(password)
    data["user_image"] = image_url
    data["created_at"] = datetime.datetime.now()
    return data
