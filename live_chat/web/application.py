from importlib import metadata

import logfire
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import UJSONResponse
from fastapi_pagination import add_pagination

from live_chat.db.utils import engine
from live_chat.services.faststream import fast_stream_router
from live_chat.settings import settings
from live_chat.web.api.router import api_router
from live_chat.web.lifespan import lifespan_setup


def get_app() -> FastAPI:
    """
    Get FastAPI application.

    This is the main constructor of an application.

    :return: application.
    """
    app = FastAPI(
        title="live_chat",
        version=metadata.version("live_chat"),
        lifespan=lifespan_setup,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        default_response_class=UJSONResponse,
        debug=True,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost",
            "http://localhost:8080",
            "http://192.168.0.104:8080",
            "http://172.28.0.7:8080",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # Main router for the API.
    app.include_router(router=api_router, prefix="/api")
    app.include_router(router=fast_stream_router)
    add_pagination(app)
    if settings.use_logfire:
        logfire.configure()
        logfire.instrument_fastapi(app)
        logfire.instrument_sqlalchemy(engine=engine.sync_engine)
    return app
