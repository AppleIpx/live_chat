import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.chat import User  # type: ignore[attr-defined]
from live_chat.db.utils import get_async_session
from live_chat.settings import settings

# Set the authorization method
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/jwt/login")


async def get_current_auth_user(
    user_requesting: User,
    token: str = Depends(oauth2_scheme),
    db_session: AsyncSession = Depends(get_async_session),
) -> bool:
    """Check user token and return whether the current authenticated user exists."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if user_requesting.is_active:
        audience = "fastapi-users:verify"
    else:
        audience = "fastapi-users:auth"
    try:
        payload = jwt.decode(
            token,
            settings.users_secret,
            audience=audience,
            algorithms=[settings.encryption_algorithm],
        )
        user_id: str = payload.get("sub")
        if not user_id:
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        ) from None
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Access Token",
        ) from None
    except jwt.PyJWTError:
        raise credentials_exception from None
    user = await db_session.get(User, user_id)
    return user is not None
