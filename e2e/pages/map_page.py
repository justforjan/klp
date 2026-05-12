from pages.klp_page import KLPPage

from playwright.sync_api import Page, expect


class MapPage(KLPPage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.title = page.get_by_text("Veranstaltungsorte")

    def url(self) -> str:
        return "/map"

    def expect_to_be_shown(self) -> "MapPage":
        expect(self.page).to_have_url(self.url())
        return self
