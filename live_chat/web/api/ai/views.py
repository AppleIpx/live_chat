from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette import EventSourceResponse
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from live_chat.db.models.chat import Chat, Task, User  # type: ignore[attr-defined]
from live_chat.db.models.enums import TaskStatus, TaskType
from live_chat.db.utils import get_async_session
from live_chat.settings import settings
from live_chat.web.ai_tools import Summarizer
from live_chat.web.ai_tools.utils.get_task import (
    delete_active_tasks_by_chat_and_user,
    get_task_by_chat_and_user,
    get_tasks_by_user,
)
from live_chat.web.api.ai.schemas import SummarizationTaskSchema
from live_chat.web.api.chat.utils import (
    get_chat_by_id,
    get_user_chats,
    validate_user_access_to_chat,
)
from live_chat.web.api.messages.constants import (
    REDIS_SSE_KEY_PREFIX,
)
from live_chat.web.api.messages.utils import (
    get_formatted_messages_by_chat,
    get_user_from_token,
    message_generator,
)
from live_chat.web.api.users.user_manager import UserManager
from live_chat.web.api.users.utils import custom_current_user, get_user_manager

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
    await delete_active_tasks_by_chat_and_user(
        db_session=db_session,
        chat_id=chat.id,
        user_id=current_user.id,
    )
    task = Task(
        type=TaskType.SUMMARIZATION,
        status=TaskStatus.IN_PROGRESS,
        user_id=current_user.id,
        chat_id=chat.id,
    )
    db_session.add(task)
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
    token: str = Query(..., alias="token"),
    db_session: AsyncSession = Depends(get_async_session),
    user_manager: UserManager = Depends(get_user_manager),
) -> EventSourceResponse:
    """Client connection to SSE."""
    current_user = await get_user_from_token(token, user_manager)
    chat = await get_chat_by_id(db_session, chat_id=chat_id)

    if chat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found",
        )

    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    user_chats = await get_user_chats(db_session, current_user=current_user)

    if chat not in user_chats:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not part of the chat",
        )

    redis_key = f"{REDIS_SSE_KEY_PREFIX}{chat.id}_{current_user.id}_summarize"
    return EventSourceResponse(message_generator(redis_key), ping=60)


@ai_router.get("/summarizations/{chat_id}")
async def get_summarization_task(
    task_status: TaskStatus,
    chat: Chat = Depends(validate_user_access_to_chat),
    current_user: User = Depends(custom_current_user),
) -> SummarizationTaskSchema:
    """Get the summarization task for this chat_id."""
    task = await get_task_by_chat_and_user(
        chat_id=chat.id,
        user_id=current_user.id,
        status=task_status,
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No summarization task found for this chat and user.",
        )

    return SummarizationTaskSchema(
        chat_id=task.chat_id,
        status=task.status.value,
        result=task.result,
        created_at=task.created_at,
        finished_at=task.finished_at,
    )


@ai_router.get("/summarizations")
async def get_summarizations_tasks(
    db_session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(custom_current_user),
) -> list[SummarizationTaskSchema]:
    """Get the current status of the summarization task."""
    tasks = await get_tasks_by_user(db_session=db_session, user_id=current_user.id)
    return [
        SummarizationTaskSchema(
            chat_id=task.chat_id,
            status=task.status.value,
            result=task.result,
            created_at=task.created_at,
            finished_at=task.finished_at,
        )
        for task in tasks
    ]
