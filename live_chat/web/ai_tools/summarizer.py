import logging
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFacePipeline
from transformers import (
    T5ForConditionalGeneration,
    T5TokenizerFast,
    pipeline,
)

from live_chat.db.models.enums import SummarizationStatus
from live_chat.web.ai_tools.hf_api_client import HuggingFaceAPIClient
from live_chat.web.ai_tools.normalizer import Normalizer
from live_chat.web.ai_tools.utils import (
    update_summarization,
)
from live_chat.web.api.ai.utils import publish_faststream_summarize
from live_chat.web.exceptions import HuggingFaceAPIClientError


class Summarizer:
    """Summarizer for summarization tasks."""

    def __init__(self) -> None:
        self.model, self.tokenizer = self._load_model_and_tokenizer()
        self.hf_pipeline = self._create_pipeline()
        self.prompt = self._create_prompt()
        self.chain = self.prompt | self.hf_pipeline | StrOutputParser()
        logging.warning("Summarizer started")
        self.normalizer = Normalizer()
        self.summarization_id: UUID
        self.user_id: UUID
        self.chat_id: UUID

    def __call__(self, summarization_id: UUID, user_id: UUID, chat_id: UUID) -> None:
        """Initialize ids for summarize."""
        self.summarization_id = summarization_id
        self.user_id = user_id
        self.chat_id = chat_id

    @staticmethod
    def _load_model_and_tokenizer(
        model_id: str = "utrobinmv/t5_summary_en_ru_zh_base_2048",
    ) -> tuple[T5ForConditionalGeneration, T5TokenizerFast]:
        """Loads the model and tokenizer."""
        model = T5ForConditionalGeneration.from_pretrained(model_id)
        tokenizer = T5TokenizerFast.from_pretrained(model_id)
        return model, tokenizer

    @staticmethod
    def _create_prompt() -> PromptTemplate:
        """Creates a template for the prompt."""
        prompt_template = (
            "Summarize the following chat conversation "
            "between two people conciseness:\n{text}"
        )
        return PromptTemplate.from_template(prompt_template)

    def _create_pipeline(self, max_length: int = 128) -> HuggingFacePipeline:
        """Creates a pipeline for resume generation."""
        summarization_pipeline = pipeline(
            "summarization",
            model=self.model,
            tokenizer=self.tokenizer,
            max_length=max_length,
            min_length=128,
            num_beams=4,
        )
        return HuggingFacePipeline(pipeline=summarization_pipeline)

    async def generate_summary_for_part(self, part: str) -> str:
        """Asynchronous summarization generation for a part of the text."""
        try:
            hf_api_client = HuggingFaceAPIClient()
            response = hf_api_client.summarize(part)
            api_result = response.json()
            if isinstance(api_result, list):
                api_result = api_result[0]
            return api_result.get("summary_text")
        except HuggingFaceAPIClientError:
            logging.warning("HuggingFace API error, started work with locale model")
            self.hf_pipeline = self._create_pipeline(max_length=len(part))
            return await self.chain.ainvoke({"text": part})

    async def _failed_summarization(self, error_message: str) -> None:
        """Send and update failed summarizations."""
        await update_summarization(
            summarization_id=self.summarization_id,
            result={"error": error_message},
            status=SummarizationStatus.ERROR,
            finished_at=datetime.now(timezone.utc),
        )
        logging.error(msg=error_message)
        await publish_faststream_summarize(
            self.user_id,
            self.chat_id,
            {"status": SummarizationStatus.ERROR, "detail": error_message},
            action="failed_summarization",
        )

    async def _update_summarization(
        self,
        result_db: dict[str, Any],
        result_sse: dict[str, Any],
        progress: float,
        action: str = "progress_summarization",
        status: SummarizationStatus = SummarizationStatus.IN_PROGRESS,
    ) -> None:
        is_finished = status == SummarizationStatus.SUCCESS
        await update_summarization(
            summarization_id=self.summarization_id,
            result=result_db,
            status=status,
            finished_at=datetime.now(timezone.utc) if is_finished else None,
            progress=progress,
        )
        await publish_faststream_summarize(
            self.user_id,
            self.chat_id,
            result_sse,
            action=action,
        )

    async def _split_dialog(self, messages_map: dict[str, str]) -> dict[str, str]:
        """Breaks the dialog into parts that are as large as possible for model."""
        date_to_text = {}
        for date, dialog in messages_map.items():
            tokens = self.tokenizer.encode(dialog)
            if len(tokens) < 256:
                continue
            parts = []
            while len(tokens) > 1450:
                part_text = self.tokenizer.decode(tokens[:1450])
                parts.append(part_text.strip())
                tokens = tokens[1450:]
            if tokens:
                final_part = self.tokenizer.decode(tokens).strip()
                parts.append(final_part)
            if len(parts) > 1:
                for i, part in enumerate(parts):
                    date_to_text[f"{date}_{i + 1}"] = part
            else:
                date_to_text[date] = parts[0]
        return date_to_text

    async def generate_summary(self, messages_map: dict[Any, str]) -> None:
        """Generate summary for a chat."""
        date_to_text = await self._split_dialog(messages_map)
        if not date_to_text:
            await self._failed_summarization("Not enough messages to generate summary")
            return
        result_data = {}
        total_parts = len(date_to_text)
        processed_parts = 0
        for date, dialog in date_to_text.items():
            normalized_dialog = await self.normalizer.normalize_text(dialog)
            if not normalized_dialog:
                error_detail = "Error with normalize messages"
            else:
                if result := await self.generate_summary_for_part(normalized_dialog):
                    result_data[date] = result
                    processed_parts += 1
                    progress = round((processed_parts / total_parts) * 100, 2)
                    await self._update_summarization(
                        result_sse={"result": {date: result}, "progress": progress},
                        result_db=result_data,
                        progress=progress,
                    )
                    continue
                error_detail = "Error with generate summary"
            await self._failed_summarization(error_detail)
            return
        await self._update_summarization(
            result_sse={"status": SummarizationStatus.SUCCESS},
            result_db=result_data,
            progress=100,
            action="finish_summarization",
            status=SummarizationStatus.SUCCESS,
        )
