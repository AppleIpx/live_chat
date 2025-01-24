from fastapi import FastAPI

from live_chat.web.ai_tools.toxic import ToxicEng, ToxicRus


def init_rus_toxilization(app: FastAPI) -> None:
    """
    Sets up the rus toxilization and stores it in the application's state.

    :param app: FastAPI application.
    """
    app.state.toxic_rus = ToxicRus()


def init_eng_toxilization(app: FastAPI) -> None:
    """
    Sets up the eng toxilization and stores it in the application's state.

    :param app: FastAPI application.
    """
    app.state.toxic_eng = ToxicEng()
