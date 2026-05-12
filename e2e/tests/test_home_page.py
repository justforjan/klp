from pages.events_page import EventsPage
from pages.map_page import MapPage


def test_home_page_visible(home_page):
    pass


def test_events_button(home_page):
    home_page.events_button.click()
    events_page = EventsPage(home_page.page)
    events_page.expect_to_be_shown()


def test_map_button(home_page):
    home_page.map_button.click()
    map_page = MapPage(home_page.page)
    map_page.expect_to_be_shown()
