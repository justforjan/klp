from abc import ABC, abstractmethod
from playwright.sync_api import Page

class PageObject(ABC):

    def __init__(self, page: Page):
        self.page = page

    @abstractmethod
    def url(self) -> str:
        pass

    @abstractmethod
    def expect_to_be_shown(self) -> 'PageObject':
        pass