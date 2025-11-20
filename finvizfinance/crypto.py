"""
.. module:: crypto
    :synopsis: crypto information

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""

from finvizfinance.util import scrap_function
from finvizfinance.market_base import MarketBase


class Crypto(MarketBase):
    """Crypto
    Getting information from the finviz crypto page.
    """

    def __init__(self):
        """initiate module"""
        super().__init__()

    def performance(self):
        """Get crypto performance table.

        Returns:
            df(pandas.DataFrame): crypto performance table
        """
        url = "https://finviz.com/crypto_performance.ashx"
        df = scrap_function(url)
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
        return super().chart(
            asset=crypto,
            timeframe=timeframe,
            urlonly=urlonly,
            chart_url_template="https://finviz.com/crypto_charts.ashx?t=",
        )
