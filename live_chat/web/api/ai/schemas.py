from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class SummarizationTaskSchema(BaseModel):
    """Schema for summarization task."""

    chat_id: UUID
    status: str
    result: dict[str, str]
    created_at: datetime
    finished_at: datetime | None
