from importlib import metadata

from fastapi import FastAPI
from fastapi.responses import UJSONResponse

from live_chat.services.faststream import fast_stream_router
from live_chat.web.api.messages.views import websocket_router
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
    )

    # Main router for the API.
    app.include_router(router=api_router, prefix="/api")
    app.include_router(router=fast_stream_router)
    app.include_router(router=websocket_router)

    return app
