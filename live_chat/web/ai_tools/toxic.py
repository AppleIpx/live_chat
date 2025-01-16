from typing import Dict, Union

from transformers import pipeline


class ToxicRus:
    """Class responsible for rus toxic detection."""

    def __init__(self) -> None:
        self.ru_toxicity = pipeline(
            "text-classification",
            model="s-nlp/russian_toxicity_classifier",
        )

    def get_toxicity(self, data: str) -> Dict[str, Union[str, float]]:
        """Method that determines rus toxicity."""
        return self.ru_toxicity(data)[0]


class ToxicEng:
    """Class responsible for eng toxic detection."""

    def __init__(self) -> None:
        self.eng_toxicity = pipeline(
            "text-classification",
            model="JungleLee/bert-toxic-comment-classification",
        )

    def get_toxicity(self, data: str) -> Dict[str, Union[str, float]]:
        """Method that determines eng toxicity."""
        return self.eng_toxicity(data)[0]
