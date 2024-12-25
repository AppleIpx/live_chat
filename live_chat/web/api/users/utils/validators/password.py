from fastapi_users import InvalidPasswordException


async def validate_password(
    email: str,
    username: str,
    password: str,
) -> bool:
    """Function that validate the password."""
    try:
        if len(password) < 8:
            raise InvalidPasswordException(
                reason="Password must be at least 8 characters long.",
            )

        if not any(char.isdigit() for char in password):
            raise InvalidPasswordException(
                reason="Password must include at least one digit.",
            )

        if not any(char.isalpha() for char in password):
            raise InvalidPasswordException(
                reason="Password must include at least one letter.",
            )

        if not any(char in "!@#$%^&*()_+-=[]{}|;':\",.<>?/`~" for char in password):
            raise InvalidPasswordException(
                reason="Password must include at least one special character.",
            )

        if password == email:
            raise InvalidPasswordException(
                reason="Password should not be similar to email.",
            )

        if password == username:  # type: ignore[union-attr]
            raise InvalidPasswordException(
                reason="Password should not be similar to username.",
            )
    except InvalidPasswordException as e:
        raise e
    except Exception as e:
        raise InvalidPasswordException(reason="An unexpected error occurred.") from e
    else:
        return True
