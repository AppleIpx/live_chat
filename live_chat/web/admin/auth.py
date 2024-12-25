import uuid

from fastapi import FastAPI
from fastapi.security import OAuth2PasswordRequestForm
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy import select
from starlette.requests import Request

from live_chat.db.models.chat import User  # type: ignore[attr-defined]
from live_chat.db.utils import async_session_maker
from live_chat.web.api.users.user_manager import UserManager
from live_chat.web.api.users.utils.custom_user_db import CustomSQLAlchemyUserDatabase

app = FastAPI()


class AdminAuth(AuthenticationBackend):
    """Authorization class in the admin panel."""

    async def login(self, request: Request) -> bool:
        """Function responsible for logging into the admin panel."""
        form = await request.form()
        username, password = str(form["username"]), str(form["password"])
        async with async_session_maker() as session:
            query = select(User).where(User.email == username)
            result = await session.execute(query)
            user_db: User = result.scalar_one_or_none()
            if user_db and user_db.is_superuser:
                user_manager = UserManager(
                    user_db=CustomSQLAlchemyUserDatabase(session, User),
                )
                request_form = OAuth2PasswordRequestForm(
                    username=username,
                    password=password,
                )
                if await user_manager.authenticate(request_form):
                    request.session.update({"token": f"{uuid.uuid4()}"})
                    return True
            return False

    async def logout(self, request: Request) -> bool:
        """Function responsible for logout out the admin panel."""
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        """A function that checks the token on every request."""
        return bool(request.session.get("token"))
