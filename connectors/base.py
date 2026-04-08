from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, TYPE_CHECKING
if TYPE_CHECKING:
    from models.schemas import SourceHealth
from loguru import logger
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from config import settings


class BaseConnector(ABC):
    source_name: str = "base"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "BankCheck/1.0 (research tool)"})
        self.timeout = settings.request_timeout

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((requests.ConnectionError, requests.Timeout)),
        reraise=True,
    )
    def _get(self, url: str, params: dict = None) -> dict:
        resp = self.session.get(url, params=params, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    @abstractmethod
    def fetch(self, **kwargs) -> Any:
        pass

    @abstractmethod
    def health_check(self) -> SourceHealth:
        pass
