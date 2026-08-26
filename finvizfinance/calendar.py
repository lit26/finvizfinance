"""
.. module:: calendar
   :synopsis: calendar.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""

import json
import re
import pandas as pd
from finvizfinance.util import web_scrap, warn_missing
from finvizfinance.exceptions import FinvizParseError

CALENDAR_URL = "https://finviz.com/calendar.ashx"


def _script_json(soup, function_name):
    """Extract the JSON argument passed to a client-side init function."""
    marker = re.compile(r"(?:window\.)?{}\s*\(".format(re.escape(function_name)))
    for script in soup.find_all("script"):
        text = script.string or script.get_text()
        match = marker.search(text)
        if match is None:
            continue
        start = match.end()
        decoder = json.JSONDecoder()
        try:
            data, _ = decoder.raw_decode(text[start:].lstrip())
        except (json.JSONDecodeError, TypeError):
            raise FinvizParseError(url=CALENDAR_URL, selector="script: {}(...)".format(function_name))
        if isinstance(data, list):
            return data
    return None


class Calendar:
    """Getting information from the finviz calendar page."""

    def __init__(self):
        pass

    def calendar(self):
        """Get economic calendar table."""
        soup = web_scrap(CALENDAR_URL)
        tables = soup.find_all("table", class_="calendar")
        if tables:
            return self._calendar_tables(tables)

        data = _script_json(soup, "FinvizInitCalendar")
        if data is None:
            raise FinvizParseError(url=CALENDAR_URL, selector="table.calendar or FinvizInitCalendar")
        rows = [self._calendar_row(row) for row in data if isinstance(row, dict)]
        # A non-empty payload that yields no readable values means finviz
        # renamed the JSON fields (Drift). Surface it instead of returning an
        # all-None table that would silently pass the live smoke check.
        if data and not any(value is not None for row in rows for value in row.values()):
            raise FinvizParseError(url=CALENDAR_URL, selector="FinvizInitCalendar fields")
        return pd.DataFrame(rows)

    @staticmethod
    def _calendar_row(row):
        """Normalize a client-rendered calendar object to the public columns."""
        def value(*keys):
            for key in keys:
                if key in row:
                    return row[key]
            return None

        day = value("date", "day")
        time = value("time", "datetime")
        if time is not None and day is not None and time != day:
            day = "{}, {}".format(day, time)
        return {
            "Datetime": day,
            "Release": value("release", "event", "title"),
            "Impact": value("impact", "importance"),
            "For": value("for", "period"),
            "Actual": value("actual"),
            "Expected": value("expected", "estimate"),
            "Prior": value("prior", "previous"),
        }

    @staticmethod
    def _calendar_tables(tables):
        frame = []
        for table in tables:
            rows = table.find_all("tr")
            if len(rows) < 2:
                continue
            check_cols = rows[1].find_all("td")
            if len(check_cols) < 3 or check_cols[2].text == "No economic releases":
                continue
            date = rows[0].find("td").text
            for row in rows[1:]:
                cols = row.find_all("td")
                if len(cols) < 8:
                    continue
                img = cols[3].find("img")
                impact = None
                if img is not None and img.get("src"):
                    match = re.findall(r"gfx/calendar/impact_(.*).gif", img["src"])
                    impact = match[0] if match else None
                if impact is None:
                    warn_missing(CALENDAR_URL, "calendar impact icon")
                frame.append({"Datetime": "{}, {}".format(date, cols[0].text), "Release": cols[2].text,
                              "Impact": impact, "For": cols[4].text, "Actual": cols[5].text,
                              "Expected": cols[6].text, "Prior": cols[7].text})
        return pd.DataFrame(frame)
