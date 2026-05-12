from __future__ import annotations

from playwright.sync_api import Page, expect
from abc import abstractmethod

from pages.page_object import PageObject


class KLPPage(PageObject):
    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        self.nav_home = page.get_by_role(
            "link", name="Kulturelle Landpartie", exact=True
        )
        self.nav_events = page.get_by_role("link", name="Termine", exact=True)
        self.nav_locations = page.get_by_role("link", name="Orte", exact=True)
        self.nav_map = page.get_by_role("link", name="Karte", exact=True)
        self.nav_favorites = page.get_by_role("link", name="Favoriten", exact=True)

    @abstractmethod
    def url(self) -> str:
        pass

    def expect_to_be_shown(self) -> "KLPPage":
        expect(self.page).to_have_url(self.url())
        return self

    def navbar_is_shown(self) -> "KLPPage":
        expect(self.nav_home).to_be_visible()
        expect(self.nav_events).to_be_visible()
        expect(self.nav_locations).to_be_visible()
        expect(self.nav_map).to_be_visible()
        expect(self.nav_favorites).to_be_visible()
        return self

    def go_to_home_page(self) -> "KLPPage":
        self.nav_home.click()
        return self

    def go_to_events_page(self) -> "KLPPage":
        self.nav_events.click()
        return self
