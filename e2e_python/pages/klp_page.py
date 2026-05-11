from __future__ import annotations

from playwright.sync_api import Page, expect
from abc import ABC, abstractmethod

from pages.page_object import PageObject


class KLPPage(ABC, PageObject):

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        self.home = page.get_by_role("link", name="Kulturelle Landpartie", exact=True)
        self.events = page.get_by_role("link", name="Termine", exact=True)
        self.locations = page.get_by_role("link", name="Orte", exact=True)
        self.map = page.get_by_role("link", name="Karte", exact=True)
        self.favorites = page.get_by_role("link", name="Favoriten", exact=True)

    @abstractmethod
    def url(self) -> str:
        pass

    def expect_to_be_shown(self) -> 'KLPPage':
        expect(self.page).to_have_url(self.url())
        return self

    def navbar_is_shown(self) -> 'KLPPage':
        expect(self.home).to_be_visible()
        expect(self.events).to_be_visible()
        expect(self.locations).to_be_visible()
        expect(self.map).to_be_visible()
        expect(self.favorites).to_be_visible()
        return self

    def go_to_home_page(self) -> 'KLPPage':
        self.home.click()
        return self


    def go_to_events_page(self) -> 'KLPPage':
        self.events.click()
        return self

