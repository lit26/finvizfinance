import json
import pandas as pd
from finvizfinance.util import web_scrap

"""
.. module:: future
   :synopsis: future.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""


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
        params = None
        if timeframe == "D":
            params = ""
        elif timeframe == "W":
            params = "?v=12"
        elif timeframe == "M":
            params = "?v=13"
        elif timeframe == "Q":
            params = "?v=14"
        elif timeframe == "HY":
            params = "?v=15"
        elif timeframe == "Y":
            params = "?v=16"
        else:
            raise ValueError("Invalid timeframe '{}'".format(timeframe))

        soup = web_scrap("https://finviz.com/futures_performance.ashx" + params)
        data = soup.text[
            soup.text.find("var rows = ")
            + 11 : soup.text.find("FinvizInitFuturesPerformance(rows);")
        ]
        data = json.loads(data.strip()[:-1])
        df = pd.DataFrame(data)
        return df
