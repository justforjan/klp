import pytest
from playwright.sync_api import Page

from pages.home_page import HomePage

@pytest.fixture
def home_page(page: Page) -> HomePage:
    page.goto("/")
    home_page = HomePage(page)
    home_page.expect_to_be_shown()
    return home_page