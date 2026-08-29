"""
.. module:: future
   :synopsis: future.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""

from __future__ import annotations

import re
from typing import Any

import pandas as pd

from finvizfinance.exceptions import FinvizParseError
from finvizfinance.util import decode_json_after, web_scrap

FUTURES_URL = "https://finviz.com/futures_performance.ashx"


def _extract_rows(soup: Any) -> Any:
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
        return decode_json_after(
            html, match.end(), FUTURES_URL, "futures performance JSON"
        )
    raise FinvizParseError(url=FUTURES_URL, selector="futures performance JSON")


class Future:
    """Getting information from the finviz future page."""

    def __init__(self) -> None:
        pass

    def performance(self, timeframe: str = "D") -> pd.DataFrame:
        """Get futures performance table."""
        timeframe_dict = {"W": 12, "M": 13, "Q": 14, "HY": 15, "Y": 16}
        params = {}
        if timeframe in timeframe_dict:
            params["v"] = timeframe_dict[timeframe]
        elif timeframe != "D":
            raise ValueError(f"Invalid timeframe '{timeframe}'")

        soup = web_scrap(FUTURES_URL, params)
        return pd.DataFrame(_extract_rows(soup))
