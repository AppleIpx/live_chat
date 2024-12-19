import logging
from datetime import datetime, timezone

from fastapi_users.jwt import decode_jwt
from sqlalchemy import select
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from live_chat.db.models.chat import User  # type: ignore[attr-defined]
from live_chat.db.utils import async_session_maker
from live_chat.web.api.users.utils import get_jwt_strategy


class UpdateLastOnlineMiddleware(BaseHTTPMiddleware):
    """Update last online for authenticated user."""

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        """Dispatch last online for authenticated user."""
        if user_token := request.headers.get("Authorization"):
            jwt_strategy = get_jwt_strategy()
            data = decode_jwt(
                user_token.split(" ")[1],
                jwt_strategy.decode_key,
                jwt_strategy.token_audience,
                algorithms=[jwt_strategy.algorithm],
            )
            if user_id := data.get("sub"):
                async with async_session_maker() as session:
                    result = await session.execute(
                        select(User).where(User.id == user_id),
                    )
                    if user := result.scalars().first():
                        now = datetime.now(timezone.utc)
                        if (
                            not user.last_online
                            or (now - user.last_online).total_seconds() >= 180
                        ):
                            user.last_online = now
                            await session.commit()
                    else:
                        logging.warning("User not found in database")
            else:
                logging.warning("User's id not found in jwt token")

        return await call_next(request)
