from finvizfinance.util import scrap_function, image_scrap_function

"""
.. module:: crypto
    :synopsis: crypto information

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""

SCREENER_TABLE_INDEX = 5


class Crypto:
    """Crypto
    Getting information from the finviz crypto page.
    Args:
        screener_table_index(int): table index of the stock screener. change only if change on finviz side.

    """

    def __init__(self, screener_table_index=SCREENER_TABLE_INDEX):
        """initiate module"""
        self._screener_table_index = screener_table_index

    def performance(self):
        """Get crypto performance table.

        Returns:
            df(pandas.DataFrame): crypto performance table
        """
        url = "https://finviz.com/crypto_performance.ashx"
        df = scrap_function(url, self._screener_table_index)
        return df

    def chart(self, crypto, timeframe="D", urlonly=False):
        """Get crypto chart.

        Args:
            crypto (str): crypto currency
            timeframe (str): choice of timeframe(5M, H, D, W, M)
            urlonly (bool): choice of downloading charts, default: downloading chart
        Returns:
            charturl(str): url for the chart
        """

        url = "https://finviz.com/crypto_charts.ashx?t=ALL&tf="
        charturl = image_scrap_function(url, crypto, timeframe, urlonly)
        return charturl
