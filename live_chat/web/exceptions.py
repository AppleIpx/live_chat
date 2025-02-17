import logging


class HuggingFaceAPIClientError(BaseException):
    """Base class for exceptions with automatic logging."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        logging.error(message)
