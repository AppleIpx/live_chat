from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import JSON


class SummarizationSchema(BaseModel):
    """Schema for summarization task."""

    chat_id: UUID
    status: str
    progress: float
    result: JSON
    created_at: datetime
    finished_at: datetime | None
