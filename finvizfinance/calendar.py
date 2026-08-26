"""
.. module:: calendar
   :synopsis: calendar.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""

import re
import pandas as pd
from finvizfinance.util import web_scrap, warn_missing
from finvizfinance.exceptions import FinvizParseError

CALENDAR_URL = "https://finviz.com/calendar.ashx"


class Calendar:
    """Calendar
    Getting information from the finviz calendar page.
    """

    def __init__(self):
        """initiate module"""
        pass

    def calendar(self):
        """Get economic calendar table.

        Returns:
            df(pandas.DataFrame): economic calendar table
        """
        soup = web_scrap(CALENDAR_URL)
        tables = soup.find_all("table", class_="calendar")
        if not tables:
            # A missing calendar table is a Structural break (Drift), not an
            # empty result — surface it instead of silently returning [].
            raise FinvizParseError(url=CALENDAR_URL, selector="table.calendar")

        frame = []
        for table in tables:
            rows = table.find_all("tr")
            if len(rows) < 2:
                continue
            check_cols = rows[1].find_all("td")
            if len(check_cols) < 3 or check_cols[2].text == "No economic releases":
                continue
            # parse date
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
                    # Missing field: keep None but surface it (Missing-field
                    # semantics), rather than silently dropping the signal.
                    warn_missing(CALENDAR_URL, "calendar impact icon")
                info_dict = {
                    "Datetime": "{}, {}".format(date, cols[0].text),
                    "Release": cols[2].text,
                    "Impact": impact,
                    "For": cols[4].text,
                    "Actual": cols[5].text,
                    "Expected": cols[6].text,
                    "Prior": cols[7].text,
                }
                frame.append(info_dict)
        return pd.DataFrame(frame)
