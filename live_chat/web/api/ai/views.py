from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette import EventSourceResponse
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from live_chat.db.models.chat import Chat  # type: ignore[attr-defined]
from live_chat.db.models.enums import SummarizationStatus
from live_chat.db.models.summarization import Summarization
from live_chat.db.models.user import User
from live_chat.db.utils import get_async_session
from live_chat.settings import settings
from live_chat.web.ai_tools.summarizer import Summarizer
from live_chat.web.ai_tools.utils import (
    delete_active_summarizations,
    get_summarization_by_chat_and_user,
    get_summarizations_by_user,
)
from live_chat.web.api.ai.schemas import SummarizationSchema
from live_chat.web.api.chat.utils import validate_user_access_to_chat
from live_chat.web.api.messages.constants import REDIS_SSE_KEY_PREFIX
from live_chat.web.api.messages.utils import (
    get_formatted_messages_by_chat,
    message_generator,
)
from live_chat.web.api.users.utils import custom_current_user
from live_chat.web.utils.validate_sse_events import validate_user_in_chat_sse

ai_router = APIRouter()


@ai_router.post("/summarizations")
async def summarize_chat(
    request: Request,
    background_tasks: BackgroundTasks,
    chat: Chat = Depends(validate_user_access_to_chat),
    current_user: User = Depends(custom_current_user),
    db_session: AsyncSession = Depends(get_async_session),
) -> JSONResponse:
    """Start summarization task."""
    if not settings.use_ai:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The use of AI is not enabled",
        )
    await delete_active_summarizations(
        db_session=db_session,
        chat_id=chat.id,
        user_id=current_user.id,
    )
    summarization = Summarization(
        status=SummarizationStatus.IN_PROGRESS,
        user_id=current_user.id,
        chat_id=chat.id,
    )
    db_session.add(summarization)
    await db_session.commit()
    messages = await get_formatted_messages_by_chat(
        chat_id=chat.id,
        current_user_id=current_user.id,
        db_session=db_session,
    )
    summarizer: Summarizer = request.app.state.summarizer
    background_tasks.add_task(
        summarizer.generate_summary,
        messages,
        current_user.id,
        chat.id,
    )
    return JSONResponse(content={"status": "Task created and processing started."})


@ai_router.get("/summarizations/stream")
async def sse_events(
    chat_id: UUID,
    user: User = Depends(validate_user_in_chat_sse),
) -> EventSourceResponse:
    """Client connection to SSE."""
    redis_key = f"{REDIS_SSE_KEY_PREFIX}{chat_id}_{user.id}_summarize"
    return EventSourceResponse(message_generator(redis_key), ping=60)


@ai_router.get("/summarizations/{chat_id}")
async def get_summarization_for_chat(
    summarization_status: SummarizationStatus,
    chat: Chat = Depends(validate_user_access_to_chat),
    current_user: User = Depends(custom_current_user),
) -> SummarizationSchema:
    """Get the summarization task for this chat_id."""
    summarization = await get_summarization_by_chat_and_user(
        chat_id=chat.id,
        user_id=current_user.id,
        status=summarization_status,
    )

    if not summarization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No summarization found for this chat and user.",
        )

    return SummarizationSchema(
        chat_id=summarization.chat_id,
        status=summarization.status.value,
        progress=summarization.progress,
        result=summarization.result,
        created_at=summarization.created_at,
        finished_at=summarization.finished_at,
    )


@ai_router.get("/summarizations")
async def get_summarizations_for_user(
    db_session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(custom_current_user),
) -> list[SummarizationSchema]:
    """Get the current status of the summarization."""
    summarizations = await get_summarizations_by_user(
        db_session=db_session,
        user_id=current_user.id,
    )
    return [
        SummarizationSchema(
            chat_id=summarization.chat_id,
            status=summarization.status.value,
            progress=summarization.progress,
            result=summarization.result,
            created_at=summarization.created_at,
            finished_at=summarization.finished_at,
        )
        for summarization in summarizations
    ]
