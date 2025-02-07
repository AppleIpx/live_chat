import asyncio
import logging

from runorm import RUNorm

logger = logging.getLogger(__name__)


class Normalizer:
    """Normalizes Russian slang for the neural network."""

    def __init__(self) -> None:
        self.normalizer = self._load_normalizer()

    @staticmethod
    def _load_normalizer(model_size: str = "medium") -> RUNorm:
        normalizer = RUNorm()
        normalizer.load(model_size=model_size, workdir="./local_cache")
        return normalizer

    async def normalize_text(self, text: str) -> str:
        """Async normalize the text to be normalized."""
        return await asyncio.to_thread(self._normalize, text)

    def _normalize(self, text: str) -> str:
        return self.normalizer.norm(text)
