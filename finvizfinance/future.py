"""
.. module:: future
   :synopsis: future.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""

import json
import pandas as pd
from finvizfinance.util import web_scrap
from finvizfinance.exceptions import FinvizParseError

FUTURES_URL = "https://finviz.com/futures_performance.ashx"


class Future:
    """Future
    Getting information from the finviz future page.
    """

    def __init__(self):
        """initiate module"""
        pass

    def performance(self, timeframe="D"):
        """Get forex performance table.

        Args:
            timeframe (str): choice of timeframe(D, W, M, Q, HY, Y)

        Returns:
            df(pandas.DataFrame): forex performance table
        """
        timeframe_dict = {"W": 12, "M": 13, "Q": 14, "HY": 15, "Y": 16}
        params = {}
        if timeframe in timeframe_dict:
            params["v"] = timeframe_dict[timeframe]
        elif timeframe != "D":
            raise ValueError("Invalid timeframe '{}'".format(timeframe))

        soup = web_scrap(FUTURES_URL, params)

        html = soup.prettify()
        start_marker = "var rows = "
        end_marker = "FinvizInitFuturesPerformance(rows);"
        if start_marker not in html or end_marker not in html:
            raise FinvizParseError(
                url=FUTURES_URL,
                selector="script: var rows = ... FinvizInitFuturesPerformance",
            )
        data = html[html.find(start_marker) + len(start_marker) : html.find(end_marker)]
        data = json.loads(data.strip()[:-1])
        df = pd.DataFrame(data)
        return df
