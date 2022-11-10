"""
.. module:: calendar
   :synopsis: calendar.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""
import re
import pandas as pd
from finvizfinance.util import web_scrap


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
        soup = web_scrap("https://finviz.com/calendar.ashx")
        tables = soup.findAll("table", class_="calendar")

        frame = []
        for table in tables:
            rows = table.findAll("tr")
            # check row
            if rows[1].findAll("td")[2].text != "No economic releases":
                # parse date
                date = rows[0].find("td").text
                for row in rows[1:]:
                    cols = row.findAll("td")
                    info_dict = {
                        "Datetime": "{}, {}".format(date, cols[0].text),
                        "Release": cols[2].text,
                        "Impact": re.findall(
                            "gfx/calendar/impact_(.*).gif", cols[3].find("img")["src"]
                        )[0],
                        "For": cols[4].text,
                        "Actual": cols[5].text,
                        "Expected": cols[6].text,
                        "Prior": cols[7].text,
                    }
                    frame.append(info_dict)
        return pd.DataFrame(frame)
