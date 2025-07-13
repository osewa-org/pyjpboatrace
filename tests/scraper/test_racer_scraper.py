from unittest.mock import Mock

import pytest

from pyjpboatrace.drivers import HTTPGetDriver
from pyjpboatrace.scraper.racer_scraper import RacerScraper

from .._utils import get_expected_json, get_mock_html


@pytest.mark.parametrize(
    "toban,tab",
    [
        (2538, "profile"),
        (2538, "back3"),
        (2538, "season"),
        (2538, "course"),
    ],
)
def test_make_url(toban: int, tab: str):
    # preparation
    base_url = "https://www.boatrace.jp/owpc/pc/data/racersearch"
    expected = f"{base_url}/{tab}?toban={toban}"
    # actual
    actual = RacerScraper.make_url(toban, tab)
    # assert
    assert actual == expected


def test_make_url_invalid_tab():
    # Test that invalid tab raises ValueError
    with pytest.raises(ValueError, match="Unknown tab type: invalid"):
        RacerScraper.make_url(2538, "invalid")


def test_get_complete_racer_data():
    """Test fetching complete racer data with all tabs"""
    # preparation
    toban = 2538
    expected = get_expected_json("expected_racer_complete.toban=2538.json")

    # Create mock driver
    mock_driver = Mock(HTTPGetDriver)

    # Mock the page source for different tabs
    def mock_get(url):
        if "profile" in url:
            mock_driver.page_source = get_mock_html("racer_profile.html")
        elif "back3" in url:
            mock_driver.page_source = get_mock_html("racer_back3.html")
        elif "season" in url:
            mock_driver.page_source = get_mock_html("racer_season.html")
        elif "course" in url:
            mock_driver.page_source = get_mock_html("racer_course.html")

    mock_driver.get.side_effect = mock_get

    # actual
    scraper = RacerScraper(driver=mock_driver)
    actual = scraper.get(toban)

    # assert
    assert actual == expected
