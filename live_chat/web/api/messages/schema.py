from pydantic import BaseModel


class DirectMessage(BaseModel):
    """Simple direct message model."""

    message: str
    recipient_id: str
