import logging
from typing import Any

import requests
from requests import ConnectionError, HTTPError, RequestException, Response, Timeout

from live_chat.settings import settings
from live_chat.web.exceptions import HuggingFaceAPIClientError


class HuggingFaceAPIClient:
    """Client for use Huggingface API."""

    def __init__(self) -> None:
        self.headers = {"Authorization": f"Bearer {settings.huggingfacehub_api_token}"}
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.api_url = settings.huggingface_api_url

    def _post(self, url: str, json: Any) -> Response:
        try:
            response = self.session.post(url=url, json=json)
            response.raise_for_status()
        except HTTPError as error:
            error_message = f"Bad response status for {url}"
            raise HuggingFaceAPIClientError(error_message) from error
        except (
            ConnectionError,
            Timeout,
            RequestException,
        ) as error:
            error_message = "Network error when fetching HuggingFace"
            raise HuggingFaceAPIClientError(error_message) from error
        else:
            message = f"Successful POST request to {url}"
            logging.info(message)
            return response

    def summarize(self, text: str) -> Response:
        """Use HuggingFace API to summarize text."""
        payload = {
            "inputs": f"Summarize following conversation by extracting key highlights, "
            f"major topics, decisions taken, and questions posed: \n{text}",
        }
        url = f"{self.api_url}/utrobinmv/t5_summary_en_ru_zh_base_2048"
        return self._post(url, payload)

    def check_toxic(self, model_name: str, data: str) -> Response:
        """Use HuggingFace API to check toxic."""
        return self._post(f"{self.api_url}/{model_name}", data)
