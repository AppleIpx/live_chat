import asyncio
import logging
from typing import Any

from live_chat.settings import settings

logger = logging.getLogger(__name__)


class Normalizer:
    """Normalizes Russian slang for the neural network."""

    def __init__(self) -> None:
        self.normalizer = self._load_normalizer()
        logging.warning("Normalizer started")

    @staticmethod
    def _load_normalizer(model_size: str = "medium") -> Any:
        if settings.use_ai:
            from runorm import RUNorm

            normalizer = RUNorm()
            normalizer.load(model_size=model_size, workdir="./local_cache")
            return normalizer
        return None

    async def normalize_text(self, text: str) -> str:
        """Async normalize the text to be normalized."""
        return await asyncio.to_thread(self._normalize, text)

    def _normalize(self, text: str) -> str:
        return self.normalizer.norm(text)
