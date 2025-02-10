import logging
from typing import Dict, Union

from transformers import pipeline


class ToxicityDetector:
    """Base class for toxicity detection."""

    def __init__(self, model_name: str) -> None:
        self.toxicity_pipeline = pipeline("text-classification", model=model_name)

    def get_toxicity(self, data: str) -> Dict[str, Union[str, float]]:
        """Method that determines toxicity."""
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
