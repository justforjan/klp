from e2e_python.pages.klp_page import KLPPage

from playwright.sync_api import Page, expect


class HomePage(KLPPage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.title = page.get_by_role("heading", name="Willkommen zur Kulturellen Landpartie")

    def url(self) -> str:
        return "/"

    def expect_to_be_shown(self) -> 'HomePage':
        expect(self.title).to_be_visible()
        expect(self.page.get_by_role("link", name="Termine durchsuchen")).to_be_visible()
        expect(self.page.get_by_role("link", name="Karte ansehen")).to_be_visible()
        return self
