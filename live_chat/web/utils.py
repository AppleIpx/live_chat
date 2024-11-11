from typing import Any

from pydantic import BaseModel, ValidationError
from starlette.websockets import WebSocket


async def validate_model(  # type: ignore[return]
    websocket: WebSocket,
    model_type: type[BaseModel],
    data: dict[str, Any],
) -> BaseModel:
    """Validate a model and return error message for user."""
    try:
        return model_type(**data)
    except ValidationError as e:
        error_message = {"error": "Invalid data", "details": e.errors()}
        await websocket.send_json(error_message)
