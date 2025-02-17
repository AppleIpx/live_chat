import logging
from typing import Dict, Union

from transformers import pipeline

from live_chat.web.ai_tools.hf_api_client import HuggingFaceAPIClient
from live_chat.web.exceptions import HuggingFaceAPIClientError


class ToxicityDetector:
    """Base class for toxicity detection."""

    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self.toxicity_pipeline = pipeline("text-classification", model=model_name)

    def get_toxicity(self, data: str) -> Dict[str, Union[str, float]]:
        """Method that determines toxicity."""
        try:
            hf_api_client = HuggingFaceAPIClient()
            response = hf_api_client.check_toxic(self.model_name, data=data)
            api_result = response.json()
            while not isinstance(api_result, dict):
                api_result = api_result[0]
            return api_result
        except HuggingFaceAPIClientError:
            logging.warning("HuggingFace API error, started work with locale model")
            return self.toxicity_pipeline(data)[0]


class ToxicRus(ToxicityDetector):
    """Class responsible for Russian toxicity detection."""

    def __init__(self) -> None:
        super().__init__("s-nlp/russian_toxicity_classifier")
        logging.warning("Russian toxicity detection started")


class ToxicEng(ToxicityDetector):
    """Class responsible for English toxicity detection."""

    def __init__(self) -> None:
        super().__init__("JungleLee/bert-toxic-comment-classification")
        logging.warning("English toxicity detection started")
