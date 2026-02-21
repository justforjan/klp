from datetime import date
import pytest
from bs4 import BeautifulSoup

from app.services.scraper import generate_event_dates, extract_time, extract_location, extract_event_details

class TestGenerateEventDates:
    def test_generate_event_dates_should_return_correct_list(self):
        # Given
        start = date.fromisoformat("2026-01-01")
        end = date.fromisoformat("2026-01-03")

        # When
        result = generate_event_dates(start, end)

        # Then
        expected = [
            "01-01",
            "02-01",
            "03-01"
        ]
        assert result == expected

    def test_generate_event_dates_should_return_one_item_if_start_equal_end(self):
        # Given
        start = date.fromisoformat("2026-01-01")
        end = date.fromisoformat("2026-01-01")

        # When
        result = generate_event_dates(start, end)

        # Then
        expected = [
            "01-01",
        ]
        assert result == expected

    def test_generate_event_dates_should_raise_exception_if_start_date_greater_end_date(self):
        # Given
        start = date.fromisoformat("2026-01-02")
        end = date.fromisoformat("2026-01-01")

        # When
        # Then
        with pytest.raises(ValueError):
            generate_event_dates(start, end)

        # <div class="row">
        #     <div><b>29.05.</b> — <nobr>09:00</nobr> | <a href="/radrouten.html#t4" target="_radrouten">Fahrradtour:<span class="num">4</span></a></div>
        #     <div><b>Bewegen am Morgen</b><br>Wir starten bewegt in den Tag. Die Mobilisierung des Körpers über sanfte Bewegungen&amp;Bewegungsimpulse aus Yoga&amp;Zeitgenössischem Tanz bringen dich in Schwung. 30 min., im Garten| tanzthe.de<br>Eintritt: Hutkasse</div>
        #     <div><a href="/orte/middefeitz.html" title="Wunderpunkt anzeigen">MIDDEFEITZ</a> (Meike Klapprodt)</div>
        # </div>

class TestParseEventRow:
    def test_extract_time_should_return_correct_time(self):
        # Given
        time_div = BeautifulSoup('<div><b>29.05.</b> — <nobr>09:00</nobr> | <a href="/radrouten.html#t4" target="_radrouten">Fahrradtour:<span class="num">4</span></a></div>')

        # When
        result = extract_time(time_div)

        # Then
        expected = ("09:00")
        assert result == expected

    def test_extract_time_should_return_none_if_no_time(self):
        # Given
        time_div = BeautifulSoup('<div><b>29.05.</b> | <a href="/radrouten.html#t4" target="_radrouten">Fahrradtour:<span class="num">4</span></a></div>')

        # When
        result = extract_time(time_div)

        # Then
        assert result is None

    def test_extract_location_should_return_correct_location(self):
        # Given
        location_div = BeautifulSoup('<div><a href="/orte/middefeitz.html" title="Wunderpunkt anzeigen">MIDDEFEITZ</a> (Meike Klapprodt)</div>')

        # When
        location_name, location_slug = extract_location(location_div)

        # Then
        expected_location_name = "MIDDEFEITZ"
        expected_location_slug = "middefeitz"
        assert location_slug == expected_location_slug
        assert location_name == expected_location_name

    def test_extract_location_should_return_none_none_if_no_link(self):
        # Given
        location_div = BeautifulSoup('<div> (Meike Klapprodt)</div>')

        # When
        location_name, location_slug = extract_location(location_div)

        # Then
        assert location_slug is None
        assert location_name is None

    def test_extract_location_should_return_none_for_slug_if_no_matching_slug(self):
        # Given
        location_div = BeautifulSoup('<div><a href="/orte/" title="Wunderpunkt anzeigen">MIDDEFEITZ</a> (Meike Klapprodt)</div>')

        # When
        location_name, location_slug = extract_location(location_div)

        # Then
        expected_location_name = "MIDDEFEITZ"
        assert location_slug is None
        assert location_name == expected_location_name

    def test_extract_location_should_return_correct_event_name_and_description(self):
        # Given
        event_description_div = BeautifulSoup('<div><b>Bewegen am Morgen</b><br>Wir starten bewegt in den Tag. <br>Eintritt: Hutkasse</div>')

        # When
        name, description = extract_event_details(event_description_div)

        # Then
        expected_name = "Bewegen am Morgen"
        expected_description = "Wir starten bewegt in den Tag. Eintritt: Hutkasse"
        assert name == expected_name
        assert description == expected_description

    def test_extract_location_should_return_default_title_if_title_is_missing(self):
        # Given
        event_description_div = BeautifulSoup('<div><br>Wir starten bewegt in den Tag. <br>Eintritt: Hutkasse</div>')

        # When
        name, description = extract_event_details(event_description_div)

        # Then
        expected_name = "Kein Titel"
        expected_description = "Wir starten bewegt in den Tag. Eintritt: Hutkasse"
        assert name == expected_name
        assert description == expected_description




