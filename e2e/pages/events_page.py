from playwright.sync_api import Page, expect
from typing import Literal

from pages.klp_page import KLPPage


class EventsPage(KLPPage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.form = page.locator("#filter-form")
        self.events_list = page.locator("div#event-list")
        self.events = page.locator("div#event-list > div")

    def url(self) -> str:
        return "/events"

    def expect_to_be_shown(self) -> "EventsPage":
        expect(self.form).to_be_visible()
        expect(self.events_list).to_be_visible()

        return self

    def expect_nr_of_search_results_to_be(self, nr: int) -> "EventsPage":
        expect(self.events).to_have_count(nr)
        return self

    def search(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
        text: str | None = None,
        location: str | None = None,
        entry_type: Literal[
            "free", "hat_collection", "fixed_price", "hat_plus_materials"
        ]
        | None = None,
        show_cancelled: Literal["", "only", "hide"] = "",
    ) -> "EventsPage":

        if start_date is not None:
            self.form.get_by_label("Von Datum").fill(start_date)
        if end_date is not None:
            self.form.get_by_label("Bis Datum").fill(end_date)
        if text is not None:
            self.form.get_by_label("Suche").fill(text)
        if location is not None:
            self.form.get_by_label("Ort").fill(location)
        if show_cancelled:
            self.form.get_by_label("show_cancelled").fill(show_cancelled)
        if entry_type is not None:
            self.form.get_by_label("Eintrittsart").fill(entry_type)

        self.form.get_by_role("button", name="Filtern").click()
        return self
