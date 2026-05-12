import pytest
from playwright.sync_api import Page

from pages.events_page import EventsPage
from pages.home_page import HomePage


@pytest.fixture
def home_page(page: Page) -> HomePage:
    page.goto("/")
    home_page = HomePage(page)
    home_page.expect_to_be_shown()
    return home_page


@pytest.fixture
def events_page(page: Page) -> EventsPage:
    page.goto("/events")
    events_page = EventsPage(page)
    events_page.expect_to_be_shown()
    return events_page
