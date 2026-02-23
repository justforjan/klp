from abc import ABC, abstractmethod
from typing import Optional
import httpx
from sqlmodel import Session


class BaseScraper(ABC):

    @abstractmethod
    async def run_initial_import(self) -> None:
        pass
