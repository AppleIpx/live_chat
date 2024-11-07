from sqlalchemy.orm import DeclarativeBase

from live_chat.db.meta import meta


class Base(DeclarativeBase):
    """Base for all models."""

    __abstract__ = True
    metadata = meta
