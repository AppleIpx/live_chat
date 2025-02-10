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

from live_chat.db.models.enums import TaskStatus
from live_chat.web.ai_tools.normalizer import Normalizer
from live_chat.web.ai_tools.utils import (
    get_task_by_chat_and_user,
    update_summarization_task,
)
from live_chat.web.api.ai.utils import publish_faststream_summarize


class Summarizer:
    """Summarizer for summarization tasks."""

    def __init__(self) -> None:
        self.model, self.tokenizer = self._load_model_and_tokenizer()
        self.hf_pipeline = self._create_pipeline()
        self.prompt = self._create_prompt()
        self.chain = self.prompt | self.hf_pipeline | StrOutputParser()
        self.normalizer = Normalizer()
        logging.warning("Summarizer started")

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
            "Summarize the shortest the following conversation, "
            "focusing on important details: {text}"
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
        self.hf_pipeline = self._create_pipeline(max_length=len(part))
        return await self.chain.ainvoke({"text": part})

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

    async def generate_summary(
        self,
        messages_map: dict[Any, str],
        user_id: UUID,
        chat_id: UUID,
    ) -> None:
        """Generate summary for a chat."""
        date_to_text = await self._split_dialog(messages_map)
        result_data = {}
        task = await get_task_by_chat_and_user(
            chat_id,
            user_id,
            status=TaskStatus.IN_PROGRESS,
        )
        if not task:
            logging.error(msg="Task was not found in db.")
            await publish_faststream_summarize(
                user_id,
                chat_id,
                {"status": TaskStatus.ERROR},
                action="finish_summarization",
            )
            return
        for date, dialog in date_to_text.items():
            normalized_dialog = await self.normalizer.normalize_text(dialog)
            if not normalized_dialog:
                error_detail = "Error with normalize messages"
            else:
                if result := await self.generate_summary_for_part(normalized_dialog):
                    result_data[date] = result
                    await update_summarization_task(task_id=task.id, result=result_data)
                    await publish_faststream_summarize(user_id, chat_id, {date: result})
                    continue
                error_detail = "Error with generate summary"
            await update_summarization_task(
                task_id=task.id,
                result={"failed_error": error_detail},
                status=TaskStatus.ERROR,
                finished_at=datetime.now(timezone.utc),
            )
            logging.error(msg=error_detail)
            await publish_faststream_summarize(
                user_id,
                chat_id,
                {"status": TaskStatus.ERROR},
                action="finish_summarization",
            )
        await update_summarization_task(
            task_id=task.id,
            result=result_data,
            status=TaskStatus.SUCCESS,
            finished_at=datetime.now(timezone.utc),
        )
        await publish_faststream_summarize(
            user_id,
            chat_id,
            {"status": TaskStatus.SUCCESS},
            action="finish_summarization",
        )
