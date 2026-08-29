"""
.. module:: calendar
   :synopsis: calendar.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any

import pandas as pd

from finvizfinance.exceptions import FinvizParseError
from finvizfinance.util import decode_json_after, warn_missing, web_scrap

CALENDAR_URL = "https://finviz.com/calendar.ashx"


def _script_json(soup: Any, function_name: str) -> list[Any] | None:
    """Extract the JSON argument passed to a client-side init function."""
    marker = re.compile(rf"(?:window\.)?{re.escape(function_name)}\s*\(")
    for script in soup.find_all("script"):
        text = script.string or script.get_text()
        match = marker.search(text)
        if match is None:
            continue
        data = decode_json_after(
            text, match.end(), CALENDAR_URL, f"script: {function_name}(...)"
        )
        if isinstance(data, list):
            return data
    return None


class Calendar:
    """Getting information from the finviz calendar page."""

    def __init__(self) -> None:
        pass

    def calendar(self) -> pd.DataFrame:
        """Get economic calendar table."""
        soup = web_scrap(CALENDAR_URL)

        # Current shape: the page is a client-rendered app and the calendar rows
        # ship as JSON inside <script id="route-init-data" type="application/json">.
        entries = self._route_init_entries(soup)
        if entries is not None:
            return self._entries_dataframe(entries)

        # Legacy shape 1: a server-rendered <table class="calendar">.
        tables = soup.find_all("table", class_="calendar")
        if tables:
            return self._calendar_tables(tables)

        # Legacy shape 2: client hydration via FinvizInitCalendar([...]).
        data = _script_json(soup, "FinvizInitCalendar")
        if data is not None:
            return self._init_dataframe(data)

        raise FinvizParseError(
            url=CALENDAR_URL,
            selector="script#route-init-data, table.calendar, or FinvizInitCalendar",
        )

    # -- current: route-init-data JSON ------------------------------------------

    @staticmethod
    def _route_init_entries(soup: Any) -> list[Any] | None:
        """Return the calendar entries embedded in the ``route-init-data`` script.

        Returns ``None`` when the script is absent, so the caller can fall back
        to the legacy page shapes. A script that *is* present but whose payload
        no longer exposes ``data.entries`` is finviz Drift and raises.
        """
        tag = soup.find("script", id="route-init-data")
        if tag is None:
            return None
        raw = tag.string or tag.get_text() or ""
        if not raw.strip():
            return None
        payload = decode_json_after(raw, 0, CALENDAR_URL, "route-init-data JSON")
        data = payload.get("data") if isinstance(payload, dict) else None
        entries = data.get("entries") if isinstance(data, dict) else None
        if not isinstance(entries, list):
            raise FinvizParseError(
                url=CALENDAR_URL, selector="route-init-data data.entries"
            )
        return entries

    @classmethod
    def _entries_dataframe(cls, entries: list[Any]) -> pd.DataFrame:
        rows = [cls._entry_row(row) for row in entries if isinstance(row, dict)]
        # A non-empty payload that yields no readable values means finviz renamed
        # the JSON fields (Drift). Surface it instead of returning an all-None
        # table that would silently pass the live smoke check.
        if entries and not any(
            value is not None for row in rows for value in row.values()
        ):
            raise FinvizParseError(
                url=CALENDAR_URL, selector="route-init-data entry fields"
            )
        return pd.DataFrame(rows)

    @classmethod
    def _entry_row(cls, entry: dict[str, Any]) -> dict[str, Any]:
        """Normalize a route-init-data calendar entry to the public columns."""

        def value(*keys: str) -> Any:
            for key in keys:
                if entry.get(key) is not None:
                    return entry[key]
            return None

        importance = value("importance", "impact")
        return {
            "Datetime": cls._format_datetime(entry),
            "Release": value("event", "release", "title"),
            "Impact": str(importance) if importance is not None else None,
            "For": value("reference", "for", "period"),
            "Actual": value("actual"),
            "Expected": value("forecast", "expected", "estimate"),
            "Prior": value("previous", "prior"),
        }

    @staticmethod
    def _format_datetime(entry: dict[str, Any]) -> Any:
        """Render the ISO ``date`` field as the historic "Day, Time" string."""
        raw = entry.get("date") or entry.get("datetime")
        if not raw:
            return None
        try:
            moment = datetime.fromisoformat(str(raw))
        except ValueError:
            # Unrecognized date format: return it verbatim rather than drop it.
            return raw
        if entry.get("allDay"):
            return moment.strftime("%a %b %d")
        return moment.strftime("%a %b %d, %I:%M %p")

    # -- legacy: FinvizInitCalendar([...]) --------------------------------------

    @classmethod
    def _init_dataframe(cls, data: list[Any]) -> pd.DataFrame:
        rows = [cls._calendar_row(row) for row in data if isinstance(row, dict)]
        # A non-empty payload that yields no readable values means finviz
        # renamed the JSON fields (Drift). Surface it instead of returning an
        # all-None table that would silently pass the live smoke check.
        if data and not any(
            value is not None for row in rows for value in row.values()
        ):
            raise FinvizParseError(
                url=CALENDAR_URL, selector="FinvizInitCalendar fields"
            )
        return pd.DataFrame(rows)

    @staticmethod
    def _calendar_row(row: Any) -> dict[str, Any]:
        """Normalize a client-rendered calendar object to the public columns."""

        def value(*keys: str) -> Any:
            for key in keys:
                if key in row:
                    return row[key]
            return None

        day = value("date", "day")
        time = value("time", "datetime")
        if time is not None and day is not None and time != day:
            day = f"{day}, {time}"
        return {
            "Datetime": day,
            "Release": value("release", "event", "title"),
            "Impact": value("impact", "importance"),
            "For": value("for", "period"),
            "Actual": value("actual"),
            "Expected": value("expected", "estimate"),
            "Prior": value("prior", "previous"),
        }

    # -- legacy: server-rendered <table class="calendar"> -----------------------

    @staticmethod
    def _calendar_tables(tables: Any) -> pd.DataFrame:
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
                frame.append(
                    {
                        "Datetime": f"{date}, {cols[0].text}",
                        "Release": cols[2].text,
                        "Impact": impact,
                        "For": cols[4].text,
                        "Actual": cols[5].text,
                        "Expected": cols[6].text,
                        "Prior": cols[7].text,
                    }
                )
        return pd.DataFrame(frame)
