"""
.. module:: future
   :synopsis: future.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""

import json
import re
import pandas as pd
from finvizfinance.util import web_scrap
from finvizfinance.exceptions import FinvizParseError

FUTURES_URL = "https://finviz.com/futures_performance.ashx"


def _extract_rows(soup):
    """Extract rows from either the legacy or current init call."""
    html = soup.prettify()
    patterns = [
        r"var\s+rows\s*=\s*",
        r"(?:window\.)?FinvizInitFuturesPerformance\s*\(\s*",
    ]
    for pattern in patterns:
        match = re.search(pattern, html)
        if match is None:
            continue
        try:
            data, _ = json.JSONDecoder().raw_decode(html[match.end():].lstrip())
        except json.JSONDecodeError:
            raise FinvizParseError(url=FUTURES_URL, selector="futures performance JSON")
        return data
    raise FinvizParseError(url=FUTURES_URL, selector="futures performance JSON")


class Future:
    """Getting information from the finviz future page."""

    def __init__(self):
        pass

    def performance(self, timeframe="D"):
        """Get futures performance table."""
        timeframe_dict = {"W": 12, "M": 13, "Q": 14, "HY": 15, "Y": 16}
        params = {}
        if timeframe in timeframe_dict:
            params["v"] = timeframe_dict[timeframe]
        elif timeframe != "D":
            raise ValueError("Invalid timeframe '{}'".format(timeframe))

        soup = web_scrap(FUTURES_URL, params)
        return pd.DataFrame(_extract_rows(soup))
