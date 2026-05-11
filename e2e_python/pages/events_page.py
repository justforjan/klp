from playwright.sync_api import Page, expect

from pages.klp_page import KLPPage


class EventsPage(KLPPage):

    def __init__(self, page: Page):
        super().__init__(page)
        self.form = page.locator("#filter-form")
        self.events_list = page.locator("div#event-list")
        self.events = page.locator("div#event-list > div")

    def url(self) -> str:
        return "/events"

    def expect_to_be_shown(self) -> 'EventsPage':
        expect(self.form).to_be_visible()
        expect(self.events_list).to_be_visible()

        return self

    def expect_nr_of_search_results_to_be(self, nr: int) -> 'EventsPage':
        expect(self.events).to_have_count(nr)
        return self

    def search(self, start_date: str, end_date: str, text: str, location: str, show_cancelled: str, entry_type: str) -> 'EventsPage':
        self.form.get_by_label("Von Datum").fill(start_date)
        self.form.get_by_label("Bis Datum").fill(end_date)
        self.form.get_by_label("Suche").fill(text)
        self.form.get_by_label("Ort").fill(location)
        self.form.get_by_label("Abgesagte Termine").fill(show_cancelled)
        self.form.get_by_label("Eintrittsart").fill(entry_type)
        self.form.get_by_role("button", name="Filtern").click()
        return self