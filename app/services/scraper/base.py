from abc import ABC, abstractmethod


class BaseScraper(ABC):

    @abstractmethod
    async def run_initial_import(self) -> None:
        pass
