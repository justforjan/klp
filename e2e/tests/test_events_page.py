from playwright.sync_api import expect

from pages.events_page import EventsPage


def test_events_page_shown(events_page: EventsPage):
    pass


def test_search_cancelled_events(events_page: EventsPage):
    events_page.search(show_cancelled="hide")
    expect(events_page.events_list).to_have_length(2)

