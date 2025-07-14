from logging import Logger, getLogger
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup, Tag
from bs4.element import NavigableString

_logger: Logger = getLogger(__name__)


def parse_html_racer_profile(html: str) -> Dict[str, Any]:
    """Parse HTML for racer profile information.

    Args:
        html (str): HTML content to parse

    Returns:
        Dict[str, Any]: Parsed racer profile information
    """
    soup = BeautifulSoup(html, "html.parser")

    # Basic racer information
    racer_info = _parse_racer_basic_info(soup)

    # Upcoming race schedule
    upcoming_races = _parse_upcoming_races(soup)

    return {"racer_info": racer_info, "upcoming_races": upcoming_races}


def _parse_racer_basic_info(soup: BeautifulSoup) -> Dict[str, Any]:
    """Parse basic racer information from HTML.

    Args:
        soup (BeautifulSoup): BeautifulSoup object of the HTML

    Returns:
        Dict[str, Any]: Basic racer information
    """
    racer_info = {}

    # Find the racer name
    racer_name_elem = soup.find("p", class_="racer1_bodyName")
    if racer_name_elem:
        racer_info["name"] = racer_name_elem.get_text(strip=True)

    # Find the racer name in kana
    racer_kana_elem = soup.find("p", class_="racer1_bodyKana")
    if racer_kana_elem:
        racer_info["name_kana"] = racer_kana_elem.get_text(strip=True)

    # Find the detailed information list
    info_list = soup.find("dl", class_="list3")
    if info_list:
        dt_elements = info_list.find_all("dt")
        dd_elements = info_list.find_all("dd")

        for dt, dd in zip(dt_elements, dd_elements):
            key = dt.get_text(strip=True)
            value = dd.get_text(strip=True)

            if key == "登録番号":
                racer_info["registration_number"] = value
            elif key == "生年月日":
                racer_info["birth_date"] = value
            elif key == "身長":
                racer_info["height"] = value
            elif key == "体重":
                racer_info["weight"] = value
            elif key == "血液型":
                racer_info["blood_type"] = value
            elif key == "支部":
                racer_info["branch"] = value
            elif key == "出身地":
                racer_info["birthplace"] = value
            elif key == "登録期":
                racer_info["registration_period"] = value
            elif key == "級別":
                racer_info["class"] = value

    return racer_info


def _parse_upcoming_races(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """Parse upcoming race schedule from HTML.

    Args:
        soup (BeautifulSoup): BeautifulSoup object of the HTML

    Returns:
        List[Dict[str, Any]]: List of upcoming races
    """
    upcoming_races = []

    # Find the race schedule table
    race_table = soup.find("table", class_="is-w832")
    if race_table:
        tbody_elements = race_table.find_all("tbody")

        for tbody in tbody_elements:
            row = tbody.find("tr")
            if row:
                cells = row.find_all("td")
                if len(cells) >= 5:
                    race_info = {}

                    # Date range
                    date_cell = cells[0]
                    date_text = date_cell.get_text(strip=True).replace("\n", " ").replace("\r", "")
                    # Clean up extra spaces and format the date range
                    date_text = " ".join(date_text.split())
                    # Add spaces around the '～' character if not present
                    if "～" in date_text:
                        date_text = date_text.replace("～", " ～ ")
                        # Remove double spaces
                        date_text = " ".join(date_text.split())
                    race_info["date_range"] = date_text

                    # Venue
                    venue_cell = cells[1]
                    venue_img = venue_cell.find("img")
                    if venue_img:
                        race_info["venue"] = venue_img.get("alt", "")

                    # Race title
                    title_cell = cells[4]
                    title_link = title_cell.find("a")
                    if title_link:
                        race_info["title"] = title_link.get_text(strip=True)
                        race_info["race_url"] = title_link.get("href", "")

                    # Race type (morning/night/etc)
                    race_type_classes = []
                    for i, cell in enumerate(cells[2:4]):  # Check grade and time cells
                        if "is-morning" in str(cell):
                            race_type_classes.append("morning")
                        elif "is-nighter" in str(cell):
                            race_type_classes.append("nighter")
                        elif "is-summer" in str(cell):
                            race_type_classes.append("summer")
                        elif "is-midnight" in str(cell):
                            race_type_classes.append("midnight")

                    race_info["race_type"] = race_type_classes

                    upcoming_races.append(race_info)

    return upcoming_races


def parse_html_racer_back3(html: str) -> Dict[str, Any]:
    """Parse HTML for racer back3 information (past 3 races performance).

    Args:
        html (str): HTML content to parse

    Returns:
        Dict[str, Any]: Parsed racer back3 information
    """
    soup = BeautifulSoup(html, "html.parser")

    back3_data = {"past_3_races": [], "recent_performance": {}}

    # Find tables with race results
    tables = soup.find_all("table", class_="is-w832")

    for table in tables:
        # Parse each race result
        rows = table.find_all("tr")
        for row in rows[1:]:  # Skip header row
            cells = row.find_all("td")
            if len(cells) >= 6:
                race_data = {
                    "date": cells[0].get_text(strip=True),
                    "venue": cells[1].get_text(strip=True),
                    "race_number": cells[2].get_text(strip=True),
                    "position": cells[3].get_text(strip=True),
                    "course": cells[4].get_text(strip=True),
                    "result": cells[5].get_text(strip=True),
                }
                back3_data["past_3_races"].append(race_data)

    # Parse recent performance summary
    summary_divs = soup.find_all("div", class_="table1")
    for div in summary_divs:
        # Extract performance metrics
        performance_data = {}
        dl_elements = div.find_all("dl")
        for dl in dl_elements:
            dt_elements = dl.find_all("dt")
            dd_elements = dl.find_all("dd")
            for dt, dd in zip(dt_elements, dd_elements):
                key = dt.get_text(strip=True)
                value = dd.get_text(strip=True)
                performance_data[key] = value

        if performance_data:
            back3_data["recent_performance"].update(performance_data)

    return back3_data


def parse_html_racer_season(html: str) -> Dict[str, Any]:
    """Parse HTML for racer season information.

    Args:
        html (str): HTML content to parse

    Returns:
        Dict[str, Any]: Parsed racer season information
    """
    soup = BeautifulSoup(html, "html.parser")

    season_data = {"season_stats": {}, "monthly_stats": []}

    # Find season statistics tables
    tables = soup.find_all("table", class_="is-w832")

    # Process each table
    for table_index, table in enumerate(tables):
        rows = table.find_all("tr")
        if len(rows) < 2:
            continue

        header_row = rows[0]
        headers = [th.get_text(strip=True) for th in header_row.find_all("th")]

        # First table is season stats, second is monthly stats
        if table_index == 0:
            # Season statistics table
            if len(rows) >= 2:
                data_row = rows[1]
                data = [td.get_text(strip=True) for td in data_row.find_all("td")]

                if headers and data and len(headers) == len(data):
                    season_stats = dict(zip(headers, data))
                    season_data["season_stats"] = season_stats

        elif table_index == 1:
            # Monthly statistics table
            for row in rows[1:]:
                cells = row.find_all("td")
                if len(cells) >= 4:
                    data = [td.get_text(strip=True) for td in cells]
                    if len(headers) == len(data):
                        monthly_stats = dict(zip(headers, data))
                        # Convert to expected format
                        monthly_data = {
                            "month": monthly_stats.get("月", ""),
                            "races": monthly_stats.get("出走回数", ""),
                            "wins": monthly_stats.get("1着回数", ""),
                            "win_rate": monthly_stats.get("勝率", ""),
                        }
                        season_data["monthly_stats"].append(monthly_data)

    return season_data


def parse_html_racer_course(html: str) -> Dict[str, Any]:
    """Parse HTML for racer course information.

    Args:
        html (str): HTML content to parse

    Returns:
        Dict[str, Any]: Parsed racer course information
    """
    soup = BeautifulSoup(html, "html.parser")

    course_data = {"course_stats": {}, "venue_stats": []}

    # Find course statistics tables
    tables = soup.find_all("table", class_="is-w832")

    for table in tables:
        # Parse course statistics by position
        rows = table.find_all("tr")
        if len(rows) > 1:
            header_row = rows[0]
            headers = [th.get_text(strip=True) for th in header_row.find_all("th")]

            for row in rows[1:]:
                cells = row.find_all("td")
                if len(cells) >= len(headers):
                    data = [td.get_text(strip=True) for td in cells]

                    if "コース" in headers[0] or "Course" in headers[0]:
                        # Course statistics
                        course_stats = dict(zip(headers, data))
                        course_number = course_stats.get("コース", course_stats.get("Course", ""))
                        if course_number:
                            course_data["course_stats"][course_number] = course_stats
                    else:
                        # Venue statistics
                        venue_stats = dict(zip(headers, data))
                        course_data["venue_stats"].append(venue_stats)

    return course_data
