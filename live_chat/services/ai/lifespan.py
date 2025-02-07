from fastapi import FastAPI

from live_chat.settings import settings
from live_chat.web.ai_tools.summarizer import Summarizer


def init_summarizer(app: FastAPI) -> None:
    """
    Sets up the summarizer and stores it in the application's state.

    :param app: FastAPI application.
    """
    if settings.use_ai:
        app.state.summarizer = Summarizer()
