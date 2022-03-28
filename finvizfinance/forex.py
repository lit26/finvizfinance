from finvizfinance.util import scrap_function, image_scrap_function

"""
.. module:: forex
   :synopsis: forex.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""

SCREENER_TABLE_INDEX = 5


class Forex:
    """Forex
    Getting information from the finviz forex page.
    Args:
        screener_table_index(int): table index of the stock screener. change only if change on finviz side.

    """

    def __init__(self, screener_table_index=SCREENER_TABLE_INDEX):
        """initiate module"""
        self._screener_table_index = screener_table_index

    def performance(self, change="percent"):
        """Get forex performance table.

        Args:
            change (str): choose an option of change(percent, PIPS)

        Returns:
            df(pandas.DataFrame): forex performance table
        """
        url = None
        if change == "percent":
            url = "https://finviz.com/forex_performance.ashx"
        elif change == "PIPS":
            url = "https://finviz.com/forex_performance.ashx?v=1&tv=2&o=-perfdaypct"
        else:
            raise ValueError("Options of change: percent(default), PIPS")
        df = scrap_function(url, self._screener_table_index)
        return df

    def chart(self, forex, timeframe="D", urlonly=False):
        """Get forex chart.

        Args:
            forex (str): foreign exchange name
            timeframe (str): choice of timeframe(5M, H, D, W, M)
            urlonly (bool): choice of downloading charts, default: downloading chart
        Returns:
            charturl(str): url for the chart
        """
        if forex == "":
            return None

        url = "https://finviz.com/forex_charts.ashx?t=ALL&tf="
        charturl = image_scrap_function(url, forex, timeframe, urlonly)
        return charturl
