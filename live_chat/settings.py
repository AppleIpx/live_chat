import enum
import os
from pathlib import Path
from tempfile import gettempdir
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict
from yarl import URL

TEMP_DIR = Path(gettempdir())


class LogLevel(str, enum.Enum):
    """Possible log levels."""

    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"


class Settings(BaseSettings):
    """
    Application settings.

    These parameters can be configured
    with environment variables.
    """

    host: str = os.getenv("HOST", "0.0.0.0")  # noqa: S104
    port: int = os.getenv("PORT", 8000)  # noqa: PLW1508
    # quantity of workers for uvicorn
    workers_count: int = os.getenv("WORKERS_COUNT", 1)  # noqa: PLW1508
    # Enable uvicorn reloading
    reload: bool = os.getenv("IS_RELOAD", False)  # noqa: PLW1508

    # Current environment
    environment: str = "dev"

    log_level: LogLevel = LogLevel.INFO
    users_secret: str = os.getenv("USERS_SECRET", "")  # type: ignore[assigment]
    # Variables for the database
    db_host: str = os.getenv("POSTGRES_HOST")  # type: ignore[assigment]
    db_port: int = int(os.getenv("POSTGRES_PORT"))  # type: ignore[assigment]
    db_user: str = os.getenv("POSTGRES_USER")  # type: ignore[assigment]
    db_pass: str = os.getenv("POSTGRES_PASSWORD")  # type: ignore[assigment]
    db_base: str = os.getenv("POSTGRES_DB")  # type: ignore[assigment]
    db_echo: bool = False

    # Variables for Redis
    redis_host: str = os.getenv("REDIS_HOST")  # type: ignore[assigment]
    redis_port: int = os.getenv("REDIS_PORT")  # type: ignore[assigment]
    redis_user: Optional[str] = None
    redis_pass: Optional[str] = None
    redis_base: Optional[int] = None

    @property
    def db_url(self) -> URL:
        """
        Assemble database URL from settings.

        :return: database URL.
        """
        return URL.build(
            scheme="postgresql+asyncpg",
            host=self.db_host,
            port=self.db_port,
            user=self.db_user,
            password=self.db_pass,
            path=f"/{self.db_base}",
        )

    @property
    def redis_url(self) -> URL:
        """
        Assemble REDIS URL from settings.

        :return: redis URL.
        """
        path = ""
        if self.redis_base is not None:
            path = f"/{self.redis_base}"
        return URL.build(
            scheme="redis",
            host=self.redis_host,
            port=self.redis_port,
            user=self.redis_user,
            password=self.redis_pass,
            path=path,
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
