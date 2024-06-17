"""
.. module:: future
   :synopsis: future.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""

import json
import pandas as pd
from finvizfinance.util import web_scrap


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

        soup = web_scrap("https://finviz.com/futures_performance.ashx", params)

        html = soup.prettify()
        data = html[
            html.find("var rows = ")
            + 11 : html.find("FinvizInitFuturesPerformance(rows);")
        ]
        data = json.loads(data.strip()[:-1])
        df = pd.DataFrame(data)
        return df
