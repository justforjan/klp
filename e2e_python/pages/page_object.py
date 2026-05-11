from abc import ABC, abstractmethod
from playwright.sync_api import Page

class PageObject(ABC, Page):

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page

    @abstractmethod
    def url(self) -> str:
        pass

    @abstractmethod
    def expect_to_be_shown(self) -> 'PageObject':
        pass