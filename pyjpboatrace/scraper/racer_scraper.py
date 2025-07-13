from logging import Logger, getLogger
from typing import Any, Dict

from selenium import webdriver

from ..const import BOATRACEJP_MAIN_URL
from ._parser import parse_html_racer_back3, parse_html_racer_course, parse_html_racer_profile, parse_html_racer_season
from .base import BaseScraper

_logger: Logger = getLogger(__name__)


class RacerScraper(BaseScraper):
    """To get racer profile information by toban (registration number)."""

    __url_format_profile = f"{BOATRACEJP_MAIN_URL}owpc/pc/data/racersearch/profile?toban={{toban}}"
    __url_format_back3 = f"{BOATRACEJP_MAIN_URL}owpc/pc/data/racersearch/back3?toban={{toban}}"
    __url_format_season = f"{BOATRACEJP_MAIN_URL}owpc/pc/data/racersearch/season?toban={{toban}}"
    __url_format_course = f"{BOATRACEJP_MAIN_URL}owpc/pc/data/racersearch/course?toban={{toban}}"

    def __init__(
        self,
        driver: webdriver.remote.webdriver.WebDriver,
        logger: Logger = _logger,
    ):
        super().__init__(driver, parse_html_racer_profile, logger)

    @classmethod
    def make_url(cls, toban: int, tab: str = "profile") -> str:
        """Make target URL.

        Args:
            toban (int): racer registration number
            tab (str): tab type ('profile', 'back3', 'season', 'course')

        Returns:
            str: URL
        """
        if tab == "profile":
            return cls.__url_format_profile.format(toban=toban)
        elif tab == "back3":
            return cls.__url_format_back3.format(toban=toban)
        elif tab == "season":
            return cls.__url_format_season.format(toban=toban)
        elif tab == "course":
            return cls.__url_format_course.format(toban=toban)
        else:
            raise ValueError(f"Unknown tab type: {tab}")

    def get(self, toban: str) -> Dict[str, Any]:
        """Get racer profile information by toban.

        Args:
            toban (str): racer registration number

        Returns:
            Dict[str, Any]: scraped data
        """
        # Get data from all tabs
        all_data = {}

        # Define tab configurations
        tab_configs = {
            "profile": parse_html_racer_profile,
            "back3": parse_html_racer_back3,
            "season": parse_html_racer_season,
            "course": parse_html_racer_course,
        }

        for tab, parser_func in tab_configs.items():
            try:
                url = self.make_url(toban, tab)
                self._logger.info(f"Fetching data from {tab} tab: {url}")
                self._driver.get(url)
                html = self._driver.page_source

                # Parse the HTML with the appropriate parser
                tab_data = parser_func(html)

                if tab == "profile":
                    # For profile, merge the data directly
                    all_data.update(tab_data)
                else:
                    # For other tabs, store under the tab name
                    all_data[tab] = tab_data

            except Exception as e:
                self._logger.warning(f"Failed to fetch data from {tab} tab: {e}")
                all_data[f"{tab}_error"] = str(e)

        return all_data
